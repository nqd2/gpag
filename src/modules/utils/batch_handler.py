"""
Batch Submission Handler for WorldQuant BRAIN.
"""

import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from modules.validator.filter import FilterResult
from modules.utils import ace_lib
from modules.utils.helpful_functions import (
    concat_is_tests,
    concat_pnl,
    get_alpha_pnl,
    get_alpha_yearly_stats,
    prettify_result,
)


@dataclass
class SubmissionRecord:
    alpha_id: int
    expression: str
    sharpe: float = 0.0
    returns_pct: float = 0.0
    turnover: float = 0.0
    fitness: float = 0.0
    holding_period: float = 0.0
    isic: float = 0.0
    decay: float = 0.0
    max_correlation: float = 0.0
    submission_time: str = ""
    batch_id: str = ""
    status: str = "pending"
    brain_alpha_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    is_stats: Optional[pd.DataFrame] = None
    is_tests: Optional[pd.DataFrame] = None
    pnl: Optional[pd.DataFrame] = None
    yearly_stats: Optional[pd.DataFrame] = None
    region: str = "USA"


@dataclass
class BatchConfig:
    max_alphas_per_batch: int = 50
    max_total_submissions: int = 500
    min_fitness_for_batch: float = 0.5
    min_sharpe_for_batch: float = 1.0
    output_dir: str = "output"
    save_expressions: bool = True
    save_metrics: bool = True
    save_batch_reports: bool = True
    default_data_delay: int = 0
    default_universe: str = "TOP3000"
    default_decay: int = 0
    default_truncation: float = 0.08
    default_neutralization: str = "SubIndustry"
    concurrent_simulations: int = 2
    pre_request_delay: float = 0.4
    pre_request_jitter: float = 0.6
    simulation_config: Optional[Dict] = None
    check_submission: bool = True
    check_self_corr: bool = True
    check_prod_corr: bool = True
    save_pnl_file: bool = False
    save_stats_file: bool = False
    save_result_file: bool = False


class BatchSubmissionHandler:
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.submission_history: List[SubmissionRecord] = []
        self.current_batch: List[SubmissionRecord] = []
        self.batch_counter = 0
        self.total_submitted = 0
        self._session = None
        os.makedirs(self.config.output_dir, exist_ok=True)

    @property
    def session(self):
        if self._session is None:
            self._session = ace_lib.start_session()
        if ace_lib.check_session_timeout(self._session) < 1000:
            self._session = ace_lib.start_session()
        return self._session

    def create_batch(self, filter_results: List[FilterResult]) -> List[SubmissionRecord]:
        self.batch_counter += 1
        batch_id = f"batch_{self.batch_counter:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_records: List[SubmissionRecord] = []
        for fr in filter_results:
            if len(batch_records) >= self.config.max_alphas_per_batch:
                break
            if self.total_submitted >= self.config.max_total_submissions:
                break
            if fr.simulation.fitness < self.config.min_fitness_for_batch:
                continue
            if fr.simulation.sharpe < self.config.min_sharpe_for_batch:
                continue
            batch_records.append(
                SubmissionRecord(
                    alpha_id=fr.individual.id,
                    expression=fr.individual.expression,
                    sharpe=fr.simulation.sharpe,
                    returns_pct=fr.simulation.returns_pct,
                    turnover=fr.simulation.turnover,
                    fitness=fr.simulation.fitness,
                    holding_period=fr.simulation.holding_period,
                    isic=fr.simulation.isic,
                    decay=fr.simulation.decay,
                    max_correlation=fr.max_correlation,
                    submission_time=datetime.now().isoformat(),
                    batch_id=batch_id,
                    status="pending",
                )
            )
        self.current_batch = batch_records
        return batch_records

    def submit_batch(self, batch: Optional[List[SubmissionRecord]] = None, simulate: bool = False) -> List[SubmissionRecord]:
        batch = batch or self.current_batch
        if not batch:
            return []
        if simulate:
            for record in batch:
                record.status = "submitted"
                record.brain_alpha_id = f"sim_alpha_{record.alpha_id:06d}"
                self.total_submitted += 1
                self.submission_history.append(record)
            return batch
        return batch

    def save_batch_report(self, batch: Optional[List[SubmissionRecord]] = None):
        batch = batch or self.current_batch
        if not batch:
            return None
        batch_id = batch[0].batch_id
        report_path = os.path.join(self.config.output_dir, f"{batch_id}_report.json")
        report = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "total_alphas": len(batch),
            "submitted": sum(1 for r in batch if r.status == "submitted"),
            "failed": sum(1 for r in batch if r.status in ("failed", "failed_checks")),
            "alphas": [
                {
                    "alpha_id": r.alpha_id,
                    "expression": r.expression,
                    "sharpe": r.sharpe,
                    "returns": r.returns_pct,
                    "turnover": r.turnover,
                    "fitness": r.fitness,
                    "status": r.status,
                    "brain_alpha_id": r.brain_alpha_id,
                }
                for r in batch
            ],
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        return report_path

    def save_expressions_file(self, batch: Optional[List[SubmissionRecord]] = None):
        batch = batch or self.current_batch
        if not batch:
            return None
        batch_id = batch[0].batch_id
        expr_path = os.path.join(self.config.output_dir, f"{batch_id}_expressions.txt")
        with open(expr_path, "w", encoding="utf-8") as f:
            for record in batch:
                f.write(record.expression + "\n")
        return expr_path

    def save_metrics_csv(self, batch: Optional[List[SubmissionRecord]] = None):
        batch = batch or self.current_batch
        if not batch:
            return None
        batch_id = batch[0].batch_id
        csv_path = os.path.join(self.config.output_dir, f"{batch_id}_metrics.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["alpha_id", "expression", "sharpe", "returns_pct", "turnover", "fitness", "status"])
            for record in batch:
                writer.writerow(
                    [
                        record.alpha_id,
                        record.expression,
                        f"{record.sharpe:.4f}",
                        f"{record.returns_pct:.6f}",
                        f"{record.turnover:.4f}",
                        f"{record.fitness:.4f}",
                        record.status,
                    ]
                )
        return csv_path

    def save_combined_report(self, results: List[Dict]):
        if not results:
            return
        batch_id = self.current_batch[0].batch_id if self.current_batch else "unknown"
        try:
            pretty_df = prettify_result(results, detailed_tests_view=False, clickable_alpha_id=True)
            pretty_df.to_html(os.path.join(self.config.output_dir, f"{batch_id}_pretty_report.html"), escape=False, index=False)
        except Exception:
            pass
        try:
            prettify_result(results).to_csv(os.path.join(self.config.output_dir, f"{batch_id}_stats.csv"), index=False)
        except Exception:
            pass
        try:
            pnl_df = concat_pnl(results)
            if not pnl_df.empty:
                pnl_df.to_csv(os.path.join(self.config.output_dir, f"{batch_id}_pnl.csv"), index=False)
        except Exception:
            pass
        try:
            tests_df = concat_is_tests(results)
            if not tests_df.empty:
                tests_df.to_csv(os.path.join(self.config.output_dir, f"{batch_id}_is_tests.csv"), index=False)
        except Exception:
            pass

    def fetch_alpha_stats(self, brain_alpha_id: str) -> Dict:
        s = self.session
        result = ace_lib.get_simulation_result_json(s, brain_alpha_id)
        is_stats = pd.DataFrame([{k: v for k, v in result["is"].items() if k != "checks"}]).assign(alpha_id=brain_alpha_id)
        is_tests = pd.DataFrame(result["is"]["checks"]).assign(alpha_id=brain_alpha_id)
        return {
            "alpha_id": brain_alpha_id,
            "region": result["settings"]["region"],
            "is_stats": is_stats,
            "is_tests": is_tests,
            "pnl": get_alpha_pnl(s, brain_alpha_id),
            "yearly_stats": get_alpha_yearly_stats(s, brain_alpha_id),
        }

    def get_submission_summary(self) -> Dict:
        if not self.submission_history:
            return {"total_submitted": 0}
        return {
            "total_submitted": self.total_submitted,
            "total_batches": self.batch_counter,
            "submitted": sum(1 for r in self.submission_history if r.status == "submitted"),
            "failed": sum(1 for r in self.submission_history if r.status in ("failed", "failed_checks")),
            "avg_sharpe": sum(r.sharpe for r in self.submission_history) / len(self.submission_history),
            "avg_fitness": sum(r.fitness for r in self.submission_history) / len(self.submission_history),
        }
