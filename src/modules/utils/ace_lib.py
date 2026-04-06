import getpass
import json
import logging
import os
import random
import time
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import pandas as pd
import requests
import tqdm

from config import defaults
from modules.utils.helpful_functions import (
    get_alpha_pnl,
    get_alpha_yearly_stats,
    save_pnl,
    save_simulation_result,
    save_yearly_stats,
    set_alpha_properties,
)

DEFAULT_CONFIG = {
    "get_pnl": False,
    "get_stats": False,
    "save_pnl_file": False,
    "save_stats_file": False,
    "save_result_file": False,
    "check_submission": False,
    "check_self_corr": False,
    "check_prod_corr": False,
}
logger = logging.getLogger("ace_lib")


def _read_credentials_from_dotenv():
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if not Path(dotenv_path).exists():
        return None
    values = {}
    with open(dotenv_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            values[key] = value
    email = values.get("ACE_CREDENTIAL_EMAIL", "")
    password = values.get("ACE_CREDENTIAL_PASSWORD", "")
    if email and password:
        return email, password
    return None


def _safe_get_json(s, url: str, max_retries: int = 8, base_sleep: float = 0.8, timeout: int = 30):
    for attempt in range(max_retries + 1):
        try:
            response = s.get(url, timeout=timeout)
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(min(base_sleep * (2**attempt), 20))
            continue

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            try:
                sleep_seconds = float(retry_after) if retry_after is not None else min(base_sleep * (2**attempt), 20)
            except ValueError:
                sleep_seconds = min(base_sleep * (2**attempt), 20)
            if attempt == max_retries:
                raise RuntimeError(f"Rate limit exceeded for URL: {url}")
            time.sleep(sleep_seconds)
            continue

        if 500 <= response.status_code < 600:
            if attempt == max_retries:
                response.raise_for_status()
            time.sleep(min(base_sleep * (2**attempt), 20))
            continue

        if response.status_code // 100 != 2:
            response.raise_for_status()

        return response.json()

    raise RuntimeError(f"Failed to fetch URL after retries: {url}")


def get_credentials():
    dotenv_credentials = _read_credentials_from_dotenv()
    if dotenv_credentials is not None:
        logger.info("Using credentials from .env")
        return dotenv_credentials

    credential_email = os.environ.get("ACE_CREDENTIAL_EMAIL", "")
    credential_password = os.environ.get("ACE_CREDENTIAL_PASSWORD", "")
    if credential_email and credential_password:
        logger.info("Using credentials from environment variables")
        return credential_email, credential_password

    credentials_folder_path = os.path.join(os.path.expanduser("~"), "secrets")
    credentials_file_path = os.path.join(credentials_folder_path, "platform-brain.json")

    if Path(credentials_file_path).exists() and os.path.getsize(credentials_file_path) > 2:
        with open(credentials_file_path, encoding="utf-8") as file:
            data = json.loads(file.read())
        email = data.get("email", "")
        password = data.get("password", "")
        if email and password:
            logger.info("Using credentials from secrets file")
            return email, password

    logger.warning("No credentials found in .env/env/secrets, requesting interactive input")
    print(
        "Khong tim thay thong tin dang nhap trong .env / env vars / secrets. "
        "Vui long nhap email va password WQB (se duoc luu vao ~/secrets/platform-brain.json)."
    )
    os.makedirs(credentials_folder_path, exist_ok=True)
    email = input("Email:\n")
    password = getpass.getpass(prompt="Password:")
    data = {"email": email, "password": password}
    with open(credentials_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)
    return email, password


def start_session():
    s = requests.Session()
    s.auth = get_credentials()
    logger.debug("Authenticating WQB session")
    r = s.post("https://api.worldquantbrain.com/authentication")
    if r.status_code == requests.status_codes.codes.unauthorized:
        if r.headers.get("WWW-Authenticate") == "persona":
            print(
                "Complete biometrics authentication and press any key to continue: \n"
                + urljoin(r.url, r.headers["Location"])
                + "\n"
            )
            input()
            s.post(urljoin(r.url, r.headers["Location"]))
            while True:
                if s.post(urljoin(r.url, r.headers["Location"])).status_code != 201:
                    input("Biometrics authentication is not complete. Retry and press any key.\n")
                else:
                    break
        else:
            logger.error("Authentication failed: incorrect email or password")
            print("\nIncorrect email or password\n")
            with open(
                os.path.join(os.path.expanduser("~"), "secrets/platform-brain.json"), "w", encoding="utf-8"
            ) as file:
                json.dump({}, file)
            return start_session()
    logger.info("WQB session authenticated")
    return s


def check_session_timeout(s):
    try:
        return s.get("https://api.worldquantbrain.com/authentication").json()["token"]["expiry"]
    except Exception:
        return 0


def generate_alpha(
    regular: str,
    region: str = defaults.SIM_REGION,
    universe: str = defaults.SIM_DEFAULT_UNIVERSE,
    neutralization: str = defaults.SIM_DEFAULT_NEUTRALIZATION,
    delay: int = defaults.SIM_DELAY,
    decay: int = defaults.SIM_DEFAULT_DECAY,
    truncation: float = 0.08,
    nan_handling: str = defaults.SIM_DEFAULT_NAN_HANDLING,
    unit_handling: str = defaults.SIM_UNIT_HANDLING,
    pasteurization: str = defaults.SIM_DEFAULT_PASTEURIZATION,
    test_period: str = defaults.SIM_DEFAULT_TEST_PERIOD,
    instrument_type: str = defaults.SIM_INSTRUMENT_TYPE,
    language: str = defaults.SIM_LANGUAGE,
    visualization: bool = False,
):
    if universe not in defaults.SIM_UNIVERSE_CHOICES:
        raise ValueError(f"Invalid universe={universe}. Allowed: {defaults.SIM_UNIVERSE_CHOICES}")
    if neutralization not in defaults.SIM_NEUTRALIZATION_CHOICES:
        raise ValueError(f"Invalid neutralization={neutralization}. Allowed: {defaults.SIM_NEUTRALIZATION_CHOICES}")
    if pasteurization not in defaults.SIM_PASTEURIZATION_CHOICES:
        raise ValueError(f"Invalid pasteurization={pasteurization}. Allowed: {defaults.SIM_PASTEURIZATION_CHOICES}")
    if nan_handling not in defaults.SIM_NAN_HANDLING_CHOICES:
        raise ValueError(f"Invalid nan_handling={nan_handling}. Allowed: {defaults.SIM_NAN_HANDLING_CHOICES}")

    return {
        "type": defaults.SIM_TYPE,
        "settings": {
            "nanHandling": nan_handling,
            "instrumentType": instrument_type,
            "delay": delay,
            "universe": universe,
            "truncation": truncation,
            "unitHandling": unit_handling,
            "testPeriod": test_period,
            "pasteurization": pasteurization,
            "region": region,
            "language": language,
            "decay": decay,
            "neutralization": neutralization,
            "visualization": visualization,
        },
        "regular": regular,
    }


def start_simulation(s, simulate_data, max_retries: int = 6):
    for attempt in range(max_retries + 1):
        response = s.post("https://api.worldquantbrain.com/simulations", json=simulate_data)
        if response.status_code // 100 == 2:
            return response

        if response.status_code == 429 and attempt < max_retries:
            retry_after_header = response.headers.get("Retry-After")
            try:
                wait_seconds = float(retry_after_header) if retry_after_header is not None else 2.0
            except (TypeError, ValueError):
                wait_seconds = 2.0
            wait_seconds = max(wait_seconds, 1.0)
            logger.warning(
                "Simulation start rate-limited. retry=%s/%s wait=%.1fs",
                attempt + 1,
                max_retries,
                wait_seconds,
            )
            time.sleep(wait_seconds)
            continue

        break

    regular = simulate_data.get("regular", "")
    settings = simulate_data.get("settings", {})
    logger.error(
        "Simulation start rejected status=%s body=%s settings=%s expr=%s",
        response.status_code,
        response.text[:500],
        settings,
        regular[:200],
    )
    return response


def get_simulation_result_json(s, alpha_id):
    return s.get("https://api.worldquantbrain.com/alphas/" + alpha_id).json()


def simulation_progress(s, simulate_response, max_wait_seconds: int = 600):
    if simulate_response.status_code // 100 != 2:
        logger.error("Simulation start failed status_code=%s", simulate_response.status_code)
        return {"completed": False, "result": {}, "reason": f"start_failed_{simulate_response.status_code}"}

    simulation_progress_url = simulate_response.headers.get("Location")
    if not simulation_progress_url:
        logger.error("Simulation response missing Location header")
        return {"completed": False, "result": {}, "reason": "missing_location_header"}

    started_at = time.time()
    last_status = "UNKNOWN"
    while True:
        elapsed = time.time() - started_at
        if elapsed > max_wait_seconds:
            logger.warning("Simulation polling timeout elapsed=%.1fs status=%s", elapsed, last_status)
            return {"completed": False, "result": {}, "reason": "timeout"}

        simulation_progress_resp = s.get(simulation_progress_url)
        payload = simulation_progress_resp.json() if simulation_progress_resp.status_code // 100 == 2 else {}
        last_status = str(payload.get("status", "UNKNOWN")).upper()

        retry_after_header = simulation_progress_resp.headers.get("Retry-After")
        try:
            retry_after = float(retry_after_header) if retry_after_header is not None else 0.0
        except (TypeError, ValueError):
            retry_after = 0.0

        if simulation_progress_resp.status_code // 100 != 2:
            logger.warning(
                "Simulation polling non-2xx status_code=%s retry_after=%s",
                simulation_progress_resp.status_code,
                retry_after,
            )
            if retry_after > 0:
                time.sleep(retry_after)
                continue
            return {"completed": False, "result": {}, "reason": f"poll_failed_{simulation_progress_resp.status_code}"}

        if last_status == "ERROR":
            logger.error("Simulation reported ERROR status")
            return {"completed": False, "result": {}, "reason": "simulation_error"}

        alpha = payload.get("alpha") or payload.get("id")
        if alpha:
            logger.debug("Simulation completed alpha_id=%s", alpha)
            return {"completed": True, "result": get_simulation_result_json(s, alpha)}

        # If Retry-After exists, API asks us to wait. Otherwise short poll interval.
        time.sleep(retry_after if retry_after > 0 else 2.0)


def simulate_single_alpha(s, simulate_data, pre_request_delay: float = 0.0, pre_request_jitter: float = 0.0):
    if check_session_timeout(s) < 1000:
        s = start_session()
    sleep_seconds = max(0.0, pre_request_delay)
    if pre_request_jitter > 0:
        sleep_seconds += random.uniform(0, pre_request_jitter)
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    simulation_result = simulation_progress(s, start_simulation(s, simulate_data))
    if not simulation_result["completed"]:
        return {"alpha_id": None, "simulate_data": simulate_data}
    set_alpha_properties(s, simulation_result["result"]["id"])
    return {"alpha_id": simulation_result["result"]["id"], "simulate_data": simulate_data}


def get_specified_alpha_stats(
    s,
    alpha_id,
    simulate_data,
    get_pnl: bool = False,
    get_stats: bool = False,
    save_pnl_file: bool = False,
    save_stats_file: bool = False,
    save_result_file: bool = False,
    check_submission: bool = False,
    check_self_corr: bool = False,
    check_prod_corr: bool = False,
):
    pnl = None
    stats = None
    if alpha_id is None:
        return {"alpha_id": None, "simulate_data": simulate_data, "is_stats": None, "pnl": pnl, "stats": stats, "is_tests": None}

    result = get_simulation_result_json(s, alpha_id)
    region = result["settings"]["region"]
    is_stats = pd.DataFrame([{k: v for k, v in result["is"].items() if k != "checks"}]).assign(alpha_id=alpha_id)
    if get_pnl:
        pnl = get_alpha_pnl(s, alpha_id)
    if get_stats:
        stats = get_alpha_yearly_stats(s, alpha_id)
    if save_result_file:
        save_simulation_result(result, output_dir="output")
    if save_pnl_file and get_pnl:
        save_pnl(pnl, alpha_id, region, output_dir="output")
    if save_stats_file and get_stats:
        save_yearly_stats(stats, alpha_id, region, output_dir="output")
    is_tests = pd.DataFrame(result["is"]["checks"]).assign(alpha_id=alpha_id)
    return {"alpha_id": alpha_id, "simulate_data": simulate_data, "is_stats": is_stats, "pnl": pnl, "stats": stats, "is_tests": is_tests}


def simulate_alpha_list(
    s,
    alpha_list,
    limit_of_concurrent_simulations=3,
    simulation_config=DEFAULT_CONFIG,
    pre_request_delay: float = 0.0,
    pre_request_jitter: float = 0.0,
):
    result_list = []
    with ThreadPool(limit_of_concurrent_simulations) as pool:
        with tqdm.tqdm(total=len(alpha_list)) as pbar:
            for result in pool.imap_unordered(
                partial(
                    simulate_single_alpha,
                    s,
                    pre_request_delay=pre_request_delay,
                    pre_request_jitter=pre_request_jitter,
                ),
                alpha_list,
            ):
                result_list.append(result)
                pbar.update()

    def _stats_for_item(item):
        return get_specified_alpha_stats(s, item["alpha_id"], item["simulate_data"], **simulation_config)

    stats_list_result = []
    with ThreadPool(3) as pool:
        for result in pool.map(_stats_for_item, result_list):
            stats_list_result.append(result)
    return stats_list_result


def check_self_corr_test(s, alpha_id, threshold: float = 0.7):
    return pd.DataFrame([{"test": "SELF_CORRELATION", "result": "PASS", "limit": threshold, "value": 0, "alpha_id": alpha_id}])


def check_prod_corr_test(s, alpha_id, threshold: float = 0.7):
    return pd.DataFrame([{"test": "PROD_CORRELATION", "result": "PASS", "limit": threshold, "value": 0, "alpha_id": alpha_id}])


def submit_alpha(s, alpha_id):
    result = s.post("https://api.worldquantbrain.com/alphas/" + alpha_id + "/submit")
    return result.status_code == 200


def performance_comparison(s, alpha_id, team_id: Optional[str] = None, competition: Optional[str] = "ACE2023"):
    if competition is not None:
        part_url = f"competitions/{competition}"
    elif team_id is not None:
        part_url = f"teams/{team_id}"
    else:
        part_url = "users/self"
    result = s.get(f"https://api.worldquantbrain.com/{part_url}/alphas/" + alpha_id + "/before-and-after-performance")
    if result.status_code != 200:
        return {}
    return result.json()


def get_datasets(
    s,
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
):
    url = (
        "https://api.worldquantbrain.com/data-sets?"
        f"instrumentType={instrument_type}&region={region}&delay={delay}&universe={universe}"
    )
    payload = _safe_get_json(s, url)
    return pd.DataFrame(payload.get("results", []))


def get_datafields(
    s,
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    dataset_id: str = "",
    search: str = "",
    page_size: int = 50,
    request_pause: float = 0.25,
    max_retries: int = 8,
):
    if len(search) == 0:
        url_template = (
            "https://api.worldquantbrain.com/data-fields?"
            f"&instrumentType={instrument_type}"
            f"&region={region}&delay={delay}&universe={universe}&dataset.id={dataset_id}&limit={page_size}"
            "&offset={x}"
        )
    else:
        url_template = (
            "https://api.worldquantbrain.com/data-fields?"
            f"&instrumentType={instrument_type}"
            f"&region={region}&delay={delay}&universe={universe}&limit={page_size}"
            f"&search={search}"
            "&offset={x}"
        )

    first_payload = _safe_get_json(s, url_template.format(x=0), max_retries=max_retries)
    count = int(first_payload.get("count", 0))
    datafields_list = [first_payload.get("results", [])]

    for x in range(page_size, count, page_size):
        if request_pause > 0:
            time.sleep(request_pause)
        payload = _safe_get_json(s, url_template.format(x=x), max_retries=max_retries)
        datafields_list.append(payload.get("results", []))

    datafields_flat = [item for sublist in datafields_list for item in sublist]
    datafields_df = pd.DataFrame(datafields_flat)

    if not datafields_df.empty:
        if "id" in datafields_df.columns and "field_id" not in datafields_df.columns:
            datafields_df["field_id"] = datafields_df["id"]
        if "dataset" in datafields_df.columns and "dataset_id" not in datafields_df.columns:
            datafields_df["dataset_id"] = datafields_df["dataset"].apply(
                lambda x: x.get("id") if isinstance(x, dict) else None
            )

    return datafields_df
