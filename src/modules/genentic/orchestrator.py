"""
Main Orchestrator for Alpha Genetic Pipeline.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from config import defaults
from modules.genentic.genetic_engine import GeneticAlphaEngine
from modules.genentic.simulator import AlphaSimulator
from modules.utils.batch_handler import BatchConfig, BatchSubmissionHandler
from modules.validator.filter import AlphaFilter, FilterConfig, FilterResult


@dataclass
class PipelineConfig:
    population_size: int = defaults.POPULATION
    generations: int = defaults.GENERATIONS
    max_tree_depth: int = 5
    max_nodes: int = 25
    min_sharpe: float = defaults.MIN_SHARPE
    min_returns: float = defaults.MIN_RETURNS
    max_turnover: float = defaults.MAX_TURNOVER
    min_turnover: float = defaults.MIN_TURNOVER
    min_fitness: float = defaults.MIN_FITNESS
    max_pairwise_correlation: float = defaults.MAX_PAIRWISE_CORRELATION
    max_alphas_per_batch: int = defaults.MAX_ALPHAS_PER_BATCH
    max_total_submissions: int = defaults.MAX_TOTAL_SUBMISSIONS
    output_dir: str = defaults.OUTPUT_DIR
    is_mock: bool = defaults.IS_MOCK
    top_k_submit: int = 3
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Optional ML-guided candidate selection to reduce expensive WQB simulations.
    # If unset/0, pipeline behavior stays unchanged.
    ml_model_path: Optional[str] = None
    ml_candidate_pool_size: int = 0


class AlphaPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger("AlphaPipeline")
        self.logger.setLevel(getattr(logging, self.config.log_level))
        self.logger.propagate = True

        self.genetic_engine = GeneticAlphaEngine(seed=42)
        self.simulator = AlphaSimulator(seed=42)
        self.alpha_filter = AlphaFilter(
            config=FilterConfig(
                min_sharpe=self.config.min_sharpe,
                min_returns=self.config.min_returns,
                min_turnover=self.config.min_turnover,
                max_turnover=self.config.max_turnover,
                min_fitness=self.config.min_fitness,
                max_pairwise_correlation=self.config.max_pairwise_correlation,
            )
        )
        self.batch_handler = BatchSubmissionHandler(
            config=BatchConfig(
                max_alphas_per_batch=self.config.max_alphas_per_batch,
                max_total_submissions=self.config.max_total_submissions,
                output_dir=self.config.output_dir,
            )
        )
        self.all_passed_results: List[FilterResult] = []
        self.generation_stats: List[Dict] = []

        self.rule_scorer = None
        if self.config.ml_model_path:
            try:
                from modules.analytics.brain_rule_scoring import load_rule_classifier

                self.rule_scorer = load_rule_classifier(self.config.ml_model_path)
                self.logger.info(
                    "Loaded ML rule classifier model=%s candidate_pool_size=%s",
                    self.config.ml_model_path,
                    self.config.ml_candidate_pool_size,
                )
            except Exception as exc:
                self.logger.warning("Failed to load ML model at %s error=%s", self.config.ml_model_path, exc)

    def run(self, target_alphas: int = 50, max_generations: int = 50) -> Dict:
        start_time = time.time()
        self.logger.info("Initializing population size=%s", self.config.population_size)
        self.genetic_engine.initialize_population(size=self.config.population_size)
        for gen in range(max_generations):
            if len(self.all_passed_results) >= target_alphas:
                self.logger.info(
                    "Target reached early at generation=%s passed=%s",
                    gen,
                    len(self.all_passed_results),
                )
                break
            self.logger.debug("Evaluating generation=%s", gen)
            gen_results = self._evaluate_population()
            valid_results = [r for r in gen_results if r.simulation.is_valid]
            fitnesses = [r.simulation.fitness for r in valid_results] if valid_results else [0.0]
            passed_count = sum(1 for r in valid_results if r.passed)
            self.generation_stats.append(
                {
                    "generation": gen,
                    "best_fitness": max(fitnesses),
                    "avg_fitness": sum(fitnesses) / len(fitnesses),
                    "passed_count": passed_count,
                    "total_evaluated": len(valid_results),
                }
            )
            self.logger.info(
                "Generation=%s evaluated=%s passed=%s best_fitness=%.4f",
                gen,
                len(valid_results),
                passed_count,
                max(fitnesses),
            )
            self.genetic_engine.evolve()

        if self.all_passed_results:
            self._submit_final_batch()
        else:
            self.logger.warning("No alpha passed filters; skipping submission")
        elapsed = time.time() - start_time
        self.logger.info("Pipeline completed in %.2fs", elapsed)
        return {
            "elapsed_seconds": elapsed,
            "total_generations": len(self.generation_stats),
            "total_alphas_passed": len(self.all_passed_results),
            "submission_summary": self.batch_handler.get_submission_summary(),
            "filter_statistics": self.alpha_filter.get_statistics(),
            "generation_stats": self.generation_stats,
        }

    def _evaluate_population(self) -> List[FilterResult]:
        results: List[FilterResult] = []
        population_to_simulate = self.genetic_engine.population

        simulated_map = {}
        if not self.config.is_mock:
            if (
                self.rule_scorer is not None
                and self.config.ml_candidate_pool_size
                and self.config.ml_candidate_pool_size > 0
                and self.config.ml_candidate_pool_size < len(population_to_simulate)
            ):
                # Score expressions first; only simulate the most promising subset.
                from modules.analytics.brain_rule_scoring import score_expression_probability

                pool_size = self.config.ml_candidate_pool_size
                scored = []
                for ind in population_to_simulate:
                    try:
                        prob = score_expression_probability(self.rule_scorer, ind.expression)
                    except Exception:
                        prob = 0.0
                    scored.append((prob, ind))
                scored.sort(key=lambda x: x[0], reverse=True)
                population_to_simulate = [ind for _, ind in scored[:pool_size]]
                self.logger.info(
                    "ML candidate selection: pool=%s selected=%s top_prob=%.4f",
                    len(self.genetic_engine.population),
                    len(population_to_simulate),
                    scored[0][0] if scored else 0.0,
                )

            simulated_map = self.batch_handler.simulate_population(population_to_simulate)

        for individual in population_to_simulate:
            sim_result = self.simulator.simulate(individual) if self.config.is_mock else simulated_map.get(individual.id)
            if sim_result is None:
                self.logger.warning("Missing simulation result for individual=%s", individual.id)
                continue
            if not sim_result.is_valid:
                self.logger.debug(
                    "Invalid simulation individual=%s reason=%s",
                    individual.id,
                    sim_result.error_message,
                )
                continue
            filter_result = self.alpha_filter.filter(individual, sim_result)
            if filter_result.passed:
                self.alpha_filter.register_passed_alpha(filter_result)
                self.all_passed_results.append(filter_result)
                self.logger.debug(
                    "Alpha passed individual=%s fitness=%.4f sharpe=%.4f",
                    individual.id,
                    sim_result.fitness,
                    sim_result.sharpe,
                )
            results.append(filter_result)
        for fr in results:
            fr.individual.fitness = fr.simulation.fitness if fr.simulation.is_valid else 0.0
        return results

    def _submit_final_batch(self):
        sorted_results = sorted(
            self.all_passed_results,
            key=lambda r: r.simulation.fitness,
            reverse=True,
        )[: self.config.top_k_submit]
        batch = self.batch_handler.create_batch(sorted_results)
        if not batch:
            self.logger.warning("No records available for final submit batch")
            return
        self.logger.info("Submitting top_k=%s alphas mode=%s", len(batch), "mock" if self.config.is_mock else "real")
        self.batch_handler.submit_batch(batch, simulate=self.config.is_mock)
        if self.batch_handler.config.save_batch_reports:
            self.batch_handler.save_batch_report(batch)
        if self.batch_handler.config.save_expressions:
            self.batch_handler.save_expressions_file(batch)
        if self.batch_handler.config.save_metrics:
            self.batch_handler.save_metrics_csv(batch)
