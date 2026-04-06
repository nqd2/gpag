"""
Alpha Simulator & Metrics Calculator.
"""

import math
import random
from typing import List, Dict
from dataclasses import dataclass, field

from modules.genentic.genetic_engine import AlphaIndividual


@dataclass
class SimulationResult:
    alpha_id: int
    expression: str
    sharpe: float = 0.0
    returns_pct: float = 0.0
    turnover: float = 0.0
    fitness: float = 0.0
    holding_period: float = 0.0
    isic: float = 0.0
    decay: float = 0.0
    is_valid: bool = True
    error_message: str = ""
    simulated_metrics: Dict = field(default_factory=dict)


class AlphaSimulator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.submitted_expressions: List[str] = []
        self.submitted_vectors: Dict[str, List[float]] = {}

    def simulate(self, individual: AlphaIndividual, universe: str = "USA", region: str = "D0") -> SimulationResult:
        result = SimulationResult(alpha_id=individual.id, expression=individual.expression)
        if not individual.expression:
            result.is_valid = False
            result.error_message = "Empty expression"
            return result
        signal_quality = self._estimate_signal_quality(individual)
        sharpe = max(-1.0, min(3.0, signal_quality * 2.0 + self.rng.gauss(0, 0.2)))
        returns_pct = max(-0.15, min(0.25, sharpe * 0.08 + self.rng.gauss(0, 0.02)))
        turnover = max(0.05, min(1.5, 0.5 + self.rng.gauss(0, 0.05)))
        fitness = sharpe * math.sqrt(abs(returns_pct) / max(turnover, 0.125))
        result.sharpe = sharpe
        result.returns_pct = returns_pct
        result.turnover = turnover
        result.fitness = fitness
        result.holding_period = max(0.5, min(20.0, 3.0 + self.rng.gauss(0, 1.0)))
        result.isic = max(-0.05, min(0.15, signal_quality * 0.08 + self.rng.gauss(0, 0.01)))
        result.decay = max(0.0, min(0.1, 0.02 * individual.tree.node_count() + self.rng.gauss(0, 0.01)))
        self.submitted_vectors[individual.expression] = self._generate_signal_vector(individual, signal_quality)
        return result

    def _estimate_signal_quality(self, individual: AlphaIndividual) -> float:
        tree = individual.tree
        depth = tree.depth()
        node_count = tree.node_count()
        quality = 0.3 + (0.2 if 2 <= depth <= 4 else -0.1) + (0.15 if 5 <= node_count <= 15 else -0.1)
        return max(0.0, min(1.0, quality + self.rng.gauss(0, 0.15)))

    def _generate_signal_vector(self, individual: AlphaIndividual, signal_quality: float) -> List[float]:
        expr_hash = hash(individual.expression)
        rng = random.Random(expr_hash)
        n = 1000
        signal = [rng.gauss(0, signal_quality) for _ in range(n)]
        noise = [rng.gauss(0, 1.0 - signal_quality * 0.5) for _ in range(n)]
        return [s + nn for s, nn in zip(signal, noise)]

    def compute_pairwise_correlation(self, expr1: str, expr2: str) -> float:
        if expr1 not in self.submitted_vectors or expr2 not in self.submitted_vectors:
            return 0.0
        v1 = self.submitted_vectors[expr1]
        v2 = self.submitted_vectors[expr2]
        if len(v1) != len(v2):
            return 0.0
        n = len(v1)
        mean1 = sum(v1) / n
        mean2 = sum(v2) / n
        cov = sum((v1[i] - mean1) * (v2[i] - mean2) for i in range(n)) / n
        std1 = math.sqrt(sum((x - mean1) ** 2 for x in v1) / n)
        std2 = math.sqrt(sum((x - mean2) ** 2 for x in v2) / n)
        if std1 < 1e-10 or std2 < 1e-10:
            return 0.0
        return cov / (std1 * std2)


class FitnessCalculator:
    @staticmethod
    def calculate(sharpe: float, returns: float, turnover: float) -> float:
        if turnover < 0:
            return 0.0
        return sharpe * math.sqrt(abs(returns) / max(turnover, 0.125))
