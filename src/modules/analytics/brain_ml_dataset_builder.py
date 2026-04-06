from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Set

import pandas as pd

from modules.analytics.brain_rule_schema import (
    DEFAULT_REQUIRED_CHECK_NAMES,
    tokenize_expression,
)
from modules.analytics.brain_rules_harvester import harvest_brain_rules_from_simulation_results


def build_rule_dataset(
    simulation_results_dir: str,
    *,
    output_csv_path: str,
    only_submitted: bool = False,
    required_check_names: Optional[Set[str]] = None,
    use_default_settings: bool = False,
) -> pd.DataFrame:
    """
    Build a flat dataset with:
      - expression text
      - token sequence
      - key metrics (sharpe/fitness/turnover/returns)
      - per-rule pass/fail
      - overall is_good_for_submit
    """

    required_check_names = required_check_names or DEFAULT_REQUIRED_CHECK_NAMES

    outcomes = harvest_brain_rules_from_simulation_results(
        simulation_results_dir,
        output_jsonl_path=None,
        required_check_names=required_check_names,
        only_submitted=only_submitted,
        use_default_settings=use_default_settings,
    )

    if not outcomes:
        raise RuntimeError(f"No simulation result JSON found in {simulation_results_dir}")

    # Stable rule vocabulary for multi-task labels.
    all_check_names: Set[str] = set()
    for row in outcomes:
        for c in row.get("checks") or []:
            if isinstance(c, dict) and c.get("name"):
                all_check_names.add(str(c["name"]))

    all_check_names_sorted = sorted(all_check_names)

    rows: List[Dict[str, Any]] = []
    for o in outcomes:
        tokens = tokenize_expression(o.get("expression") or "")
        checks_by_name = {}
        for c in o.get("checks") or []:
            if isinstance(c, dict) and c.get("name"):
                checks_by_name[str(c["name"])] = str(c.get("result") or "")

        row: Dict[str, Any] = {
            "alpha_id": o.get("alpha_id"),
            "expression": o.get("expression"),
            "tokens": " ".join(tokens),
            "token_count": len(tokens),
            "sharpe": o.get("sharpe"),
            "fitness": o.get("fitness"),
            "turnover": o.get("turnover"),
            "returns_pct": o.get("returns_pct"),
            "instrument_type": o.get("instrument_type"),
            "region": o.get("region"),
            "universe": o.get("universe"),
            "delay": o.get("delay"),
            "decay": o.get("decay"),
            "truncation": o.get("truncation"),
            "neutralization": o.get("neutralization"),
            "pasteurization": o.get("pasteurization"),
            "nan_handling": o.get("nan_handling"),
            "unit_handling": o.get("unit_handling"),
            "language": o.get("language"),
            "test_period": o.get("test_period"),
            "is_submitted": o.get("is_submitted"),
            "required_checks_passed": o.get("required_checks_passed"),
            "is_good_for_submit": o.get("is_good_for_submit"),
        }

        for rule_name in all_check_names_sorted:
            res = checks_by_name.get(rule_name)
            row[f"rule_{rule_name}_pass"] = 1 if res == "PASS" else 0

        rows.append(row)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_csv_path) or ".", exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    return df


def build_rule_dataset_cli(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build ML dataset from BRAIN simulation_results JSON artifacts.")
    parser.add_argument("--input-dir", type=str, required=True, help="Path to output/simulation_results/")
    parser.add_argument("--output", type=str, required=True, help="Output CSV path")
    parser.add_argument("--only-submitted", type=_str2bool, default=False, help="Only rows where dateSubmitted/status indicates submission")
    parser.add_argument(
        "--use-default-settings",
        type=_str2bool,
        default=False,
        help="Override extracted settings with defaults from src/config/defaults.py",
    )
    args = parser.parse_args(argv)

    build_rule_dataset(
        args.input_dir,
        output_csv_path=args.output,
        only_submitted=args.only_submitted,
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
    raise SystemExit(build_rule_dataset_cli())

