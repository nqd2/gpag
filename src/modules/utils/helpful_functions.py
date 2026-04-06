import json
import os
import time

import pandas as pd


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


def make_clickable_alpha_id(alpha_id):
    url = "https://platform.worldquantbrain.com/alpha/"
    return f'<a href="{url}{alpha_id}">{alpha_id}</a>'


def prettify_result(result, detailed_tests_view=False, clickable_alpha_id: bool = False):
    list_of_is_stats = [result[x]["is_stats"] for x in range(len(result)) if result[x]["is_stats"] is not None]
    is_stats_df = pd.concat(list_of_is_stats).reset_index(drop=True)
    is_stats_df = is_stats_df.sort_values("fitness", ascending=False)
    expressions = {
        result[x]["alpha_id"]: result[x]["simulate_data"]["regular"]
        for x in range(len(result))
        if result[x]["is_stats"] is not None
    }
    expression_df = pd.DataFrame(list(expressions.items()), columns=["alpha_id", "expression"])
    list_of_is_tests = [result[x]["is_tests"] for x in range(len(result)) if result[x]["is_tests"] is not None]
    is_tests_df = pd.concat(list_of_is_tests).reset_index(drop=True)
    if detailed_tests_view:
        cols = ["limit", "result", "value"]
        is_tests_df["details"] = is_tests_df[cols].to_dict(orient="records")
        is_tests_df = is_tests_df.pivot(index="alpha_id", columns="name", values="details").reset_index()
    else:
        is_tests_df = is_tests_df.pivot(index="alpha_id", columns="name", values="result").reset_index()
    alpha_stats = pd.merge(is_stats_df, expression_df, on="alpha_id")
    alpha_stats = pd.merge(alpha_stats, is_tests_df, on="alpha_id")
    alpha_stats.columns = alpha_stats.columns.str.replace("(?<=[a-z])(?=[A-Z])", "_", regex=True).str.lower()
    if clickable_alpha_id:
        return alpha_stats.style.format({"alpha_id": make_clickable_alpha_id})
    return alpha_stats


def concat_pnl(result):
    list_of_pnls = [result[x]["pnl"] for x in range(len(result)) if result[x]["pnl"] is not None]
    return pd.concat(list_of_pnls).reset_index()


def concat_is_tests(result):
    is_tests_list = [result[x]["is_tests"] for x in range(len(result)) if result[x]["is_tests"] is not None]
    return pd.concat(is_tests_list).reset_index(drop=True)


def save_simulation_result(result):
    alpha_id = result["id"]
    region = result["settings"]["region"]
    folder_path = "simulation_results/"
    file_path = os.path.join(folder_path, f"{alpha_id}_{region}")
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(result, file)


def set_alpha_properties(
    s,
    alpha_id,
    name: str = None,
    color: str = None,
    selection_desc: str = "None",
    combo_desc: str = "None",
    tags=["22_3_2026"],
):
    params = {
        "color": color,
        "name": name,
        "tags": tags,
        "category": None,
        "regular": {"description": None},
        "combo": {"description": combo_desc},
        "selection": {"description": selection_desc},
    }
    s.patch("https://api.worldquantbrain.com/alphas/" + alpha_id, json=params)


def save_pnl(pnl_df, alpha_id, region):
    folder_path = "alphas_pnl/"
    file_path = os.path.join(folder_path, f"{alpha_id}_{region}")
    os.makedirs(folder_path, exist_ok=True)
    pnl_df.to_csv(file_path)


def save_yearly_stats(yearly_stats, alpha_id, region):
    folder_path = "yearly_stats/"
    file_path = os.path.join(folder_path, f"{alpha_id}_{region}")
    os.makedirs(folder_path, exist_ok=True)
    yearly_stats.to_csv(file_path, index=False)


def get_alpha_pnl(s, alpha_id):
    while True:
        result = s.get("https://api.worldquantbrain.com/alphas/" + alpha_id + "/recordsets/pnl")
        if "retry-after" in result.headers:
            time.sleep(float(result.headers["Retry-After"]))
        else:
            break
    pnl = result.json().get("records", 0)
    if pnl == 0:
        return pd.DataFrame()
    return (
        pd.DataFrame(pnl, columns=["Date", "Pnl"])
        .assign(alpha_id=alpha_id, Date=lambda x: pd.to_datetime(x.Date, format="%Y-%m-%d"))
        .set_index("Date")
    )


def get_alpha_yearly_stats(s, alpha_id):
    while True:
        result = s.get("https://api.worldquantbrain.com/alphas/" + alpha_id + "/recordsets/yearly-stats")
        if "retry-after" in result.headers:
            time.sleep(float(result.headers["Retry-After"]))
        else:
            break
    stats = result.json()
    if stats.get("records", 0) == 0:
        return pd.DataFrame()
    columns = [dct["name"] for dct in stats["schema"]["properties"]]
    return pd.DataFrame(stats["records"], columns=columns).assign(alpha_id=alpha_id)
