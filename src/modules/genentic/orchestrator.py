"""
Main Orchestrator for Alpha Genetic Pipeline.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from modules.genentic.genetic_engine import GeneticAlphaEngine
from modules.genentic.simulator import AlphaSimulator
from modules.utils.batch_handler import BatchConfig, BatchSubmissionHandler
from modules.validator.filter import AlphaFilter, FilterConfig, FilterResult


@dataclass
class PipelineConfig:
    population_size: int = 200
    generations: int = 50
    max_tree_depth: int = 5
    max_nodes: int = 25
    min_sharpe: float = 1.0
    min_returns: float = 0.01
    max_turnover: float = 0.7
    min_fitness: float = 0.5
    max_pairwise_correlation: float = 0.70
    max_alphas_per_batch: int = 50
    max_total_submissions: int = 500
    output_dir: str = "output"
    log_level: str = "INFO"
    log_file: Optional[str] = None


class AlphaPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger("AlphaPipeline")
        self.logger.setLevel(getattr(logging, self.config.log_level))
        if not self.logger.handlers:
            self.logger.addHandler(logging.StreamHandler())

        self.genetic_engine = GeneticAlphaEngine(seed=42)
        self.simulator = AlphaSimulator(seed=42)
        self.alpha_filter = AlphaFilter(
            config=FilterConfig(
                min_sharpe=self.config.min_sharpe,
                min_returns=self.config.min_returns,
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

    def run(self, target_alphas: int = 50, max_generations: int = 50) -> Dict:
        start_time = time.time()
        self.logger.info("Initializing population...")
        self.genetic_engine.initialize_population(size=self.config.population_size)
        for gen in range(max_generations):
            if len(self.all_passed_results) >= target_alphas:
                break
            gen_results = self._evaluate_population()
            valid_results = [r for r in gen_results if r.simulation.is_valid]
            fitnesses = [r.simulation.fitness for r in valid_results] if valid_results else [0.0]
            self.generation_stats.append(
                {
                    "generation": gen,
                    "best_fitness": max(fitnesses),
                    "avg_fitness": sum(fitnesses) / len(fitnesses),
                    "passed_count": sum(1 for r in valid_results if r.passed),
                    "total_evaluated": len(valid_results),
                }
            )
            self.genetic_engine.evolve()

        if self.all_passed_results:
            self._submit_final_batch()
        elapsed = time.time() - start_time
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
        for individual in self.genetic_engine.population:
            sim_result = self.simulator.simulate(individual)
            if not sim_result.is_valid:
                continue
            filter_result = self.alpha_filter.filter(individual, sim_result)
            if filter_result.passed:
                self.alpha_filter.register_passed_alpha(filter_result)
                self.all_passed_results.append(filter_result)
            results.append(filter_result)
        for fr in results:
            fr.individual.fitness = fr.simulation.fitness if fr.simulation.is_valid else 0.0
        return results

    def _submit_final_batch(self):
        sorted_results = sorted(self.all_passed_results, key=lambda r: r.simulation.fitness, reverse=True)
        batch = self.batch_handler.create_batch(sorted_results)
        if not batch:
            return
        self.batch_handler.submit_batch(batch, simulate=True)
        if self.batch_handler.config.save_batch_reports:
            self.batch_handler.save_batch_report(batch)
        if self.batch_handler.config.save_expressions:
            self.batch_handler.save_expressions_file(batch)
        if self.batch_handler.config.save_metrics:
            self.batch_handler.save_metrics_csv(batch)
