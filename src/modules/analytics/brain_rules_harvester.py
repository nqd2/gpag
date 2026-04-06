from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Set

from config import defaults
from modules.analytics.brain_rule_schema import (
    DEFAULT_REQUIRED_CHECK_NAMES,
    BrainRuleOutcome,
    extract_primary_expression,
    is_alpha_good_for_submit,
    normalize_checks,
)


def _parse_alpha_id_from_filename(file_path: str) -> str:
    # output/simulation_results/<alpha_id>_<region>.json
    base = os.path.basename(file_path)
    # Strip extension if any (though current files appear extension-less)
    base = base.split(".", 1)[0]
    parts = base.rsplit("_", 1)
    return parts[0] if parts else base


def parse_simulation_result_json(
    payload: Dict[str, Any],
    *,
    required_check_names: Set[str],
    use_default_settings: bool = False,
) -> BrainRuleOutcome:
    alpha_id = str(payload.get("id") or "")
    if not alpha_id:
        alpha_id = str(payload.get("alpha_id") or "")

    # Pass full payload so extractor can read `regular.code` correctly.
    expression = extract_primary_expression(payload)
    # region IS Testing metrics
    is_section = payload.get("is") if isinstance(payload.get("is"), dict) else {}
    settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
    if use_default_settings:
        settings = {
            "instrumentType": defaults.SIM_INSTRUMENT_TYPE,
            "region": defaults.SIM_REGION,
            "universe": defaults.SIM_DEFAULT_UNIVERSE,
            "delay": defaults.SIM_DELAY,
            "decay": defaults.SIM_DEFAULT_DECAY,
            "truncation": defaults.SIM_DEFAULT_TRUNCATION,
            "neutralization": defaults.SIM_DEFAULT_NEUTRALIZATION,
            "pasteurization": defaults.SIM_DEFAULT_PASTEURIZATION,
            "nanHandling": defaults.SIM_DEFAULT_NAN_HANDLING,
            "unitHandling": defaults.SIM_UNIT_HANDLING,
            "language": defaults.SIM_LANGUAGE,
            "testPeriod": defaults.SIM_DEFAULT_TEST_PERIOD,
        }
    sharpe = is_section.get("sharpe")
    fitness = is_section.get("fitness")
    turnover = is_section.get("turnover")
    returns_pct = is_section.get("returns")

    raw_checks = is_section.get("checks")
    checks = normalize_checks(raw_checks)

    required_passed, is_good = is_alpha_good_for_submit(checks, required_check_names=required_check_names)

    # Detect submit state. Status UN/ SUBMITTED depends on payload; dateSubmitted is usually present on submitted alphas.
    date_submitted = payload.get("dateSubmitted")
    status = payload.get("status")
    is_submitted = bool(date_submitted) or str(status).upper() in {"SUBMITTED", "PROD", "APPROVED"}

    out = BrainRuleOutcome(
        alpha_id=alpha_id,
        expression=expression,
        sharpe=float(sharpe) if isinstance(sharpe, (int, float, str)) and str(sharpe).strip() != "" else None,
        fitness=float(fitness) if isinstance(fitness, (int, float, str)) and str(fitness).strip() != "" else None,
        turnover=float(turnover) if isinstance(turnover, (int, float, str)) and str(turnover).strip() != "" else None,
        returns_pct=float(returns_pct) if isinstance(returns_pct, (int, float, str)) and str(returns_pct).strip() != "" else None,
        instrument_type=str(settings.get("instrumentType") or "") or None,
        region=str(settings.get("region") or "") or None,
        universe=str(settings.get("universe") or "") or None,
        delay=int(settings["delay"]) if isinstance(settings.get("delay"), (int, float)) else None,
        decay=int(settings["decay"]) if isinstance(settings.get("decay"), (int, float)) else None,
        truncation=float(settings["truncation"]) if isinstance(settings.get("truncation"), (int, float, str)) and str(settings.get("truncation")).strip() != "" else None,
        neutralization=str(settings.get("neutralization") or "") or None,
        pasteurization=str(settings.get("pasteurization") or "") or None,
        nan_handling=str(settings.get("nanHandling") or "") or None,
        unit_handling=str(settings.get("unitHandling") or "") or None,
        language=str(settings.get("language") or "") or None,
        test_period=str(settings.get("testPeriod") or "") or None,
        checks=checks,
        is_submitted=is_submitted,
        required_checks_passed=required_passed,
        is_good_for_submit=is_good,
    )
    return out


def harvest_brain_rules_from_simulation_results(
    simulation_results_dir: str,
    *,
    output_jsonl_path: Optional[str] = None,
    required_check_names: Optional[Set[str]] = None,
    only_submitted: bool = False,
    max_files: Optional[int] = None,
    use_default_settings: bool = False,
) -> List[Dict[str, Any]]:
    """
    Offline "harvester" that parses local BRAIN simulation result JSON artifacts.

    This works because `batch_handler.simulate_expression()` persists `wqb_result`
    into `simulation_results/<brain_alpha_id>_<region>`.
    """

    required_check_names = required_check_names or DEFAULT_REQUIRED_CHECK_NAMES
    required_check_names = set(required_check_names)

    if not os.path.isdir(simulation_results_dir):
        raise FileNotFoundError(f"Simulation results dir not found: {simulation_results_dir}")

    outcomes: List[Dict[str, Any]] = []
    file_count = 0

    for name in sorted(os.listdir(simulation_results_dir)):
        file_path = os.path.join(simulation_results_dir, name)
        if not os.path.isfile(file_path):
            continue
        if name.startswith("."):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception:
            # Skip corrupted/unexpected files
            continue

        alpha_id = str(payload.get("id") or "") or _parse_alpha_id_from_filename(file_path)
        if only_submitted:
            date_submitted = payload.get("dateSubmitted")
            status = str(payload.get("status") or "").upper()
            if not date_submitted and status not in {"SUBMITTED", "PROD", "APPROVED"}:
                continue

        outcome = parse_simulation_result_json(
            payload,
            required_check_names=required_check_names,
            use_default_settings=use_default_settings,
        )
        if not outcome.alpha_id:
            outcome.alpha_id = alpha_id

        outcomes.append(asdict(outcome))
        file_count += 1
        if max_files is not None and file_count >= max_files:
            break

    if output_jsonl_path:
        os.makedirs(os.path.dirname(output_jsonl_path) or ".", exist_ok=True)
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for row in outcomes:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return outcomes


def harvest_brain_rules_from_simulation_results_cli(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Harvest BRAIN rule pass/fail from local simulation_results JSON.")
    parser.add_argument("--input-dir", type=str, required=True, help="Path to output/simulation_results/")
    parser.add_argument("--output", type=str, required=False, help="Output jsonl path")
    parser.add_argument("--only-submitted", type=_str2bool, default=False, help="Filter only submitted alphas")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument(
        "--use-default-settings",
        type=_str2bool,
        default=False,
        help="Override extracted settings with defaults from src/config/defaults.py",
    )
    args = parser.parse_args(argv)

    harvest_brain_rules_from_simulation_results(
        args.input_dir,
        output_jsonl_path=args.output,
        only_submitted=args.only_submitted,
        max_files=args.max_files,
        use_default_settings=args.use_default_settings,
    )
    return 0


def _str2bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


if __name__ == "__main__":
    raise SystemExit(harvest_brain_rules_from_simulation_results_cli())

