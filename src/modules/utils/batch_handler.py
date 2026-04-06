"""
Batch Submission Handler for WorldQuant BRAIN.
"""

import csv
import json
import logging
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from config import defaults
from modules.genentic.genetic_engine import AlphaIndividual
from modules.genentic.simulator import SimulationResult
from modules.validator.filter import FilterResult
from modules.utils import ace_lib
from modules.utils.helpful_functions import (
    concat_is_tests,
    concat_pnl,
    get_alpha_pnl,
    get_alpha_yearly_stats,
    prettify_result,
    save_pnl,
    save_simulation_result,
    save_yearly_stats,
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
    max_alphas_per_batch: int = defaults.MAX_ALPHAS_PER_BATCH
    max_total_submissions: int = defaults.MAX_TOTAL_SUBMISSIONS
    min_fitness_for_batch: float = defaults.MIN_FITNESS_FOR_BATCH
    min_sharpe_for_batch: float = defaults.MIN_SHARPE_FOR_BATCH
    output_dir: str = defaults.OUTPUT_DIR
    save_expressions: bool = True
    save_metrics: bool = True
    save_batch_reports: bool = True
    default_data_delay: int = defaults.SIM_DELAY
    default_universe: str = defaults.SIM_DEFAULT_UNIVERSE
    default_decay: int = defaults.SIM_DEFAULT_DECAY
    default_truncation: float = defaults.SIM_DEFAULT_TRUNCATION
    default_neutralization: str = defaults.SIM_DEFAULT_NEUTRALIZATION
    default_test_period: str = defaults.SIM_DEFAULT_TEST_PERIOD
    default_pasteurization: str = defaults.SIM_DEFAULT_PASTEURIZATION
    default_nan_handling: str = defaults.SIM_DEFAULT_NAN_HANDLING
    default_unit_handling: str = defaults.SIM_UNIT_HANDLING
    default_instrument_type: str = defaults.SIM_INSTRUMENT_TYPE
    default_language: str = defaults.SIM_LANGUAGE
    default_region: str = defaults.SIM_REGION
    concurrent_simulations: int = defaults.CONCURRENT_SIMULATIONS
    pre_request_delay: float = defaults.PRE_REQUEST_DELAY
    pre_request_jitter: float = defaults.PRE_REQUEST_JITTER
    simulation_config: Optional[Dict] = None
    check_submission: bool = True
    check_self_corr: bool = True
    check_prod_corr: bool = True
    save_pnl_file: bool = True
    save_stats_file: bool = True
    save_result_file: bool = True


class BatchSubmissionHandler:
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.submission_history: List[SubmissionRecord] = []
        self.current_batch: List[SubmissionRecord] = []
        self.batch_counter = 0
        self.total_submitted = 0
        self._session = None
        self.logger = logging.getLogger("BatchSubmissionHandler")
        os.makedirs(self.config.output_dir, exist_ok=True)

    @property
    def session(self):
        if self._session is None:
            self.logger.info("Starting WQB session")
            self._session = ace_lib.start_session()
        if ace_lib.check_session_timeout(self._session) < 1000:
            self.logger.warning("WQB session near timeout; refreshing")
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
                    brain_alpha_id=fr.simulation.simulated_metrics.get("brain_alpha_id"),
                )
            )
        self.current_batch = batch_records
        self.logger.info("Created batch id=%s size=%s", batch_id, len(batch_records))
        return batch_records

    @staticmethod
    def _get_metric(metrics: Dict, *keys, default: float = 0.0) -> float:
        for key in keys:
            if key in metrics and metrics[key] is not None:
                try:
                    return float(metrics[key])
                except (TypeError, ValueError):
                    continue
        return default

    def simulate_population(self, individuals: List[AlphaIndividual]) -> Dict[int, SimulationResult]:
        if not individuals:
            return {}
        self.logger.info(
            "Simulating population concurrently size=%s workers=%s",
            len(individuals),
            self.config.concurrent_simulations,
        )
        result_by_id: Dict[int, SimulationResult] = {}
        max_workers = max(1, self.config.concurrent_simulations)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.simulate_expression, ind.id, ind.expression, None): ind.id
                for ind in individuals
            }
            for future in as_completed(future_map):
                alpha_id = future_map[future]
                try:
                    result_by_id[alpha_id] = future.result()
                except Exception as exc:
                    self.logger.error("Population simulation future failed alpha_id=%s error=%s", alpha_id, exc)
                    result_by_id[alpha_id] = SimulationResult(
                        alpha_id=alpha_id,
                        expression="",
                        is_valid=False,
                        error_message=str(exc),
                    )
        return result_by_id

    def simulate_expression(self, alpha_id: int, expression: str, session=None) -> SimulationResult:
        result = SimulationResult(alpha_id=alpha_id, expression=expression)
        if not expression:
            result.is_valid = False
            result.error_message = "Empty expression"
            return result
        try:
            self.logger.debug("Start simulation alpha_id=%s", alpha_id)
            active_session = session or ace_lib.start_session()
            simulation_payload = ace_lib.generate_alpha(
                regular=expression,
                region=self.config.default_region,
                universe=self.config.default_universe,
                neutralization=self.config.default_neutralization,
                delay=self.config.default_data_delay,
                decay=self.config.default_decay,
                truncation=self.config.default_truncation,
                nan_handling=self.config.default_nan_handling,
                unit_handling=self.config.default_unit_handling,
                pasteurization=self.config.default_pasteurization,
                instrument_type=self.config.default_instrument_type,
                language=self.config.default_language,
                test_period=self.config.default_test_period,
            )
            simulation_response = ace_lib.start_simulation(active_session, simulation_payload)
            progress = ace_lib.simulation_progress(active_session, simulation_response)
            if not progress.get("completed"):
                fail_reason = progress.get("reason", "unknown")
                self.logger.warning("Simulation not completed alpha_id=%s", alpha_id)
                result.is_valid = False
                result.error_message = f"Simulation failed: {fail_reason}"
                return result

            wqb_result = progress.get("result", {})
            is_metrics = wqb_result.get("is", {})
            brain_alpha_id = wqb_result.get("id")
            region = wqb_result.get("settings", {}).get("region", "USA")
            sharpe = self._get_metric(is_metrics, "sharpe")
            returns_pct = self._get_metric(is_metrics, "returns", "returnsPct", "returns_pct")
            turnover = self._get_metric(is_metrics, "turnover")
            fitness = self._get_metric(is_metrics, "fitness")
            # IS Testing checks (pass/fail/pending) used to enforce additional BRAIN rules.
            raw_checks = is_metrics.get("checks") if isinstance(is_metrics, dict) else None
            if isinstance(raw_checks, list):
                result.brain_checks = [c for c in raw_checks if isinstance(c, dict)]
            if fitness == 0.0 and turnover >= 0:
                fitness = sharpe * math.sqrt(abs(returns_pct) / max(turnover, 0.125))

            result.sharpe = sharpe
            result.returns_pct = returns_pct
            result.turnover = turnover
            result.fitness = fitness
            result.holding_period = self._get_metric(is_metrics, "holdingPeriod", "holding_period")
            result.isic = self._get_metric(is_metrics, "isic")
            result.decay = self._get_metric(
                is_metrics,
                "decay",
                default=float(wqb_result.get("settings", {}).get("decay", self.config.default_decay)),
            )
            result.simulated_metrics = {"brain_alpha_id": brain_alpha_id}

            # Persist raw simulation artifacts by default for later analysis.
            if self.config.save_result_file:
                save_simulation_result(wqb_result, output_dir=self.config.output_dir)
            if self.config.save_pnl_file and brain_alpha_id:
                pnl_df = get_alpha_pnl(active_session, brain_alpha_id)
                save_pnl(pnl_df, brain_alpha_id, region, output_dir=self.config.output_dir)
            if self.config.save_stats_file and brain_alpha_id:
                yearly_stats_df = get_alpha_yearly_stats(active_session, brain_alpha_id)
                save_yearly_stats(yearly_stats_df, brain_alpha_id, region, output_dir=self.config.output_dir)

            self.logger.info(
                "Simulation success alpha_id=%s sharpe=%.4f fitness=%.4f",
                alpha_id,
                result.sharpe,
                result.fitness,
            )
            return result
        except Exception as exc:
            self.logger.error("Simulation error alpha_id=%s error=%s", alpha_id, exc)
            result.is_valid = False
            result.error_message = f"WQB simulation error: {exc}"
            return result

    def submit_batch(self, batch: Optional[List[SubmissionRecord]] = None, simulate: bool = False) -> List[SubmissionRecord]:
        batch = batch or self.current_batch
        if not batch:
            self.logger.warning("submit_batch called with empty batch")
            return []
        if simulate:
            self.logger.info("Submitting batch in mock mode size=%s", len(batch))
            for record in batch:
                record.status = "submitted"
                record.brain_alpha_id = f"sim_alpha_{record.alpha_id:06d}"
                self.total_submitted += 1
                self.submission_history.append(record)
            return batch
        self.logger.info("Submitting batch in real mode size=%s", len(batch))
        for record in batch:
            if not record.brain_alpha_id:
                record.status = "failed"
                record.rejection_reason = "Missing WQB alpha id"
                self.logger.error("Missing brain alpha id local_id=%s", record.alpha_id)
                self.submission_history.append(record)
                continue
            try:
                ok = ace_lib.submit_alpha(self.session, record.brain_alpha_id)
                if ok:
                    record.status = "submitted"
                    self.total_submitted += 1
                    self.logger.info("Submit success alpha_id=%s brain_id=%s", record.alpha_id, record.brain_alpha_id)
                    # Fetch updated IS Testing/production status right after submit,
                    # so downstream rule harvesting can distinguish PASS/FAIL for submitted alphas.
                    if self.config.save_result_file:
                        try:
                            updated = ace_lib.get_simulation_result_json(self.session, record.brain_alpha_id)
                            save_simulation_result(updated, output_dir=self.config.output_dir)
                        except Exception as exc:
                            self.logger.warning(
                                "Failed to refresh brain alpha json after submit alpha_id=%s brain_id=%s error=%s",
                                record.alpha_id,
                                record.brain_alpha_id,
                                exc,
                            )
                else:
                    record.status = "failed"
                    record.rejection_reason = "WQB submit failed"
                    self.logger.error("Submit failed alpha_id=%s brain_id=%s", record.alpha_id, record.brain_alpha_id)
            except Exception as exc:
                record.status = "failed"
                record.rejection_reason = str(exc)
                self.logger.error("Submit exception alpha_id=%s error=%s", record.alpha_id, exc)
            self.submission_history.append(record)
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
