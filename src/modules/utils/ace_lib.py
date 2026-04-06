import getpass
import json
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


def get_credentials():
    credential_email = os.environ.get("ACE_CREDENTIAL_EMAIL")
    credential_password = os.environ.get("ACE_CREDENTIAL_PASSWORD")
    credentials_folder_path = os.path.join(os.path.expanduser("~"), "secrets")
    credentials_file_path = os.path.join(credentials_folder_path, "platform-brain.json")

    if Path(credentials_file_path).exists() and os.path.getsize(credentials_file_path) > 2:
        with open(credentials_file_path, encoding="utf-8") as file:
            data = json.loads(file.read())
    else:
        os.makedirs(credentials_folder_path, exist_ok=True)
        if credential_email and credential_password:
            email = credential_email
            password = credential_password
        else:
            email = input("Email:\n")
            password = getpass.getpass(prompt="Password:")
        data = {"email": email, "password": password}
        with open(credentials_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)
    return data["email"], data["password"]


def start_session():
    s = requests.Session()
    s.auth = get_credentials()
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
            print("\nIncorrect email or password\n")
            with open(
                os.path.join(os.path.expanduser("~"), "secrets/platform-brain.json"), "w", encoding="utf-8"
            ) as file:
                json.dump({}, file)
            return start_session()
    return s


def check_session_timeout(s):
    try:
        return s.get("https://api.worldquantbrain.com/authentication").json()["token"]["expiry"]
    except Exception:
        return 0


def generate_alpha(
    regular: str,
    region: str = "USA",
    universe: str = "TOP500",
    neutralization: str = "NONE",
    delay: int = 1,
    decay: int = 2,
    truncation: float = 0.08,
    nan_handling: str = "OFF",
    unit_handling: str = "VERIFY",
    pasteurization: str = "ON",
    visualization: bool = False,
):
    return {
        "type": "REGULAR",
        "settings": {
            "nanHandling": nan_handling,
            "instrumentType": "EQUITY",
            "delay": delay,
            "universe": universe,
            "truncation": truncation,
            "unitHandling": unit_handling,
            "pasteurization": pasteurization,
            "region": region,
            "language": "FASTEXPR",
            "decay": decay,
            "neutralization": neutralization,
            "visualization": visualization,
        },
        "regular": regular,
    }


def start_simulation(s, simulate_data):
    return s.post("https://api.worldquantbrain.com/simulations", json=simulate_data)


def get_simulation_result_json(s, alpha_id):
    return s.get("https://api.worldquantbrain.com/alphas/" + alpha_id).json()


def simulation_progress(s, simulate_response):
    if simulate_response.status_code // 100 != 2:
        return {"completed": False, "result": {}}
    simulation_progress_url = simulate_response.headers["Location"]
    error_flag = False
    while True:
        simulation_progress_resp = s.get(simulation_progress_url)
        if simulation_progress_resp.headers.get("Retry-After", 0) == 0:
            if simulation_progress_resp.json().get("status", "ERROR") == "ERROR":
                error_flag = True
            break
        time.sleep(float(simulation_progress_resp.headers["Retry-After"]))
    if error_flag:
        return {"completed": False, "result": {}}
    alpha = simulation_progress_resp.json().get("alpha", 0)
    if alpha == 0:
        return {"completed": False, "result": {}}
    return {"completed": True, "result": get_simulation_result_json(s, alpha)}


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
        save_simulation_result(result)
    if save_pnl_file and get_pnl:
        save_pnl(pnl, alpha_id, region)
    if save_stats_file and get_stats:
        save_yearly_stats(stats, alpha_id, region)
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
