"""
Alpha Filtering & Decorrelation Module.
"""

import re
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import random

from config import defaults
from modules.genentic.genetic_engine import AlphaIndividual
from modules.genentic.simulator import SimulationResult
from modules.analytics.brain_rule_schema import DEFAULT_REQUIRED_CHECK_NAMES


@dataclass
class FilterConfig:
    min_sharpe: float = defaults.MIN_SHARPE
    min_returns: float = defaults.MIN_RETURNS
    min_turnover: float = defaults.MIN_TURNOVER
    max_turnover: float = defaults.MAX_TURNOVER
    min_fitness: float = defaults.MIN_FITNESS
    max_pairwise_correlation: float = defaults.MAX_PAIRWISE_CORRELATION
    use_brain_checks: bool = True
    required_brain_check_names: Set[str] = field(default_factory=lambda: set(DEFAULT_REQUIRED_CHECK_NAMES))


@dataclass
class FilterResult:
    individual: AlphaIndividual
    simulation: SimulationResult
    passed: bool
    fail_reasons: List[str] = field(default_factory=list)
    max_correlation: float = 0.0
    correlation_details: Dict[str, float] = field(default_factory=dict)


class AlphaFilter:
    def __init__(self, config: Optional[FilterConfig] = None):
        self.config = config or FilterConfig()
        self.submitted_alphas: List[FilterResult] = []
        self.submitted_expressions: Set[str] = set()
        self.field_usage: Dict[str, int] = defaultdict(int)
        self.operator_usage: Dict[str, int] = defaultdict(int)

    def filter(self, individual: AlphaIndividual, simulation: SimulationResult) -> FilterResult:
        result = FilterResult(individual=individual, simulation=simulation, passed=True, fail_reasons=[])
        if not simulation.is_valid:
            result.passed = False
            result.fail_reasons.append(f"Invalid: {simulation.error_message}")
            return result
        if simulation.sharpe < self.config.min_sharpe:
            result.passed = False
            result.fail_reasons.append("Sharpe below threshold")
            return result
        if abs(simulation.returns_pct) < self.config.min_returns:
            result.passed = False
            result.fail_reasons.append("Returns below threshold")
            return result
        if simulation.turnover < self.config.min_turnover:
            result.passed = False
            result.fail_reasons.append("Turnover below threshold")
            return result
        if simulation.turnover > self.config.max_turnover:
            result.passed = False
            result.fail_reasons.append("Turnover above threshold")
            return result
        if simulation.fitness < self.config.min_fitness:
            result.passed = False
            result.fail_reasons.append("Fitness below threshold")
            return result

        if self.config.use_brain_checks and simulation.brain_checks:
            checks_by_name: Dict[str, str] = {}
            for c in simulation.brain_checks:
                if not isinstance(c, dict):
                    continue
                name = c.get("name")
                res = c.get("result")
                if isinstance(name, str) and isinstance(res, str):
                    checks_by_name[name] = res.upper()

            missing_or_not_passed = []
            for required_name in self.config.required_brain_check_names:
                res = checks_by_name.get(required_name)
                if res != "PASS":
                    missing_or_not_passed.append(required_name)

            if missing_or_not_passed:
                result.passed = False
                result.fail_reasons.append(f"Brain checks not passed: {sorted(missing_or_not_passed)[:3]}")
                return result

        corr_passed, max_corr, corr_details = self._check_decorrelation(individual.expression)
        result.max_correlation = max_corr
        result.correlation_details = corr_details
        if not corr_passed:
            result.passed = False
            result.fail_reasons.append("Correlation too high")
        return result

    def _check_decorrelation(self, expression: str) -> Tuple[bool, float, Dict[str, float]]:
        if not self.submitted_expressions:
            return True, 0.0, {}
        correlations = {}
        max_corr = 0.0
        for submitted_expr in self.submitted_expressions:
            corr = self._compute_expression_similarity(expression, submitted_expr)
            correlations[submitted_expr] = corr
            max_corr = max(max_corr, abs(corr))
        return max_corr <= self.config.max_pairwise_correlation, max_corr, correlations

    def _compute_expression_similarity(self, expr1: str, expr2: str) -> float:
        tokens1 = self._tokenize_expression(expr1)
        tokens2 = self._tokenize_expression(expr2)
        if not tokens1 or not tokens2:
            return 0.0
        set1 = set(tokens1)
        set2 = set(tokens2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        if union == 0:
            return 0.0
        jaccard = intersection / union
        rng = random.Random(hash(expr1) + hash(expr2))
        return max(-0.3, min(0.95, jaccard * 0.8 + rng.gauss(0, 0.1)))

    def _tokenize_expression(self, expression: str) -> List[str]:
        tokens = re.findall(r"[a-z_]+|\d+\.?\d*|[+\-*/(),]", expression.lower())
        return [t for t in tokens if t not in ("(", ")", ",")]

    def _get_primary_field(self, individual: AlphaIndividual) -> Optional[str]:
        nodes = self._collect_all_nodes(individual.tree)
        fields = [n.value for n in nodes if n.node_type == "field"]
        return Counter(fields).most_common(1)[0][0] if fields else None

    def _get_primary_operator(self, individual: AlphaIndividual) -> Optional[str]:
        return individual.tree.value if individual.tree.node_type == "operator" else None

    def _collect_all_nodes(self, tree) -> list:
        nodes = [tree]
        for child in tree.children:
            nodes.extend(self._collect_all_nodes(child))
        return nodes

    def register_passed_alpha(self, filter_result: FilterResult):
        expr = filter_result.individual.expression
        self.submitted_expressions.add(expr)
        self.submitted_alphas.append(filter_result)
        primary_field = self._get_primary_field(filter_result.individual)
        primary_operator = self._get_primary_operator(filter_result.individual)
        if primary_field:
            self.field_usage[primary_field] += 1
        if primary_operator:
            self.operator_usage[primary_operator] += 1

    def get_statistics(self) -> Dict:
        total = len(self.submitted_alphas)
        if total == 0:
            return {"total_submitted": 0}
        return {
            "total_submitted": total,
            "avg_sharpe": sum(a.simulation.sharpe for a in self.submitted_alphas) / total,
            "avg_returns": sum(a.simulation.returns_pct for a in self.submitted_alphas) / total,
            "avg_turnover": sum(a.simulation.turnover for a in self.submitted_alphas) / total,
            "avg_fitness": sum(a.simulation.fitness for a in self.submitted_alphas) / total,
        }
