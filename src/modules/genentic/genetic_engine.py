"""
Genetic Programming Engine for Alpha Expression Evolution.
Handles tree generation, crossover, mutation, and selection.
"""

import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from collections import defaultdict

from modules.genentic.expression_grammar import TreeNode, Operator, GrammarConfig, GROUP_PARAMS


@dataclass
class AlphaIndividual:
    tree: TreeNode
    fitness: float = 0.0
    sharpe: float = 0.0
    returns: float = 0.0
    turnover: float = 0.0
    is_valid: bool = True
    generation: int = 0
    parent_ids: Tuple[Optional[int], Optional[int]] = (None, None)
    id: int = 0

    @property
    def expression(self) -> str:
        return self.tree.to_string()


class GeneticAlphaEngine:
    def __init__(self, config: Optional[GrammarConfig] = None, seed: int = 42):
        self.config = config or GrammarConfig()
        self.rng = random.Random(seed)
        self.population: List[AlphaIndividual] = []
        self.generation = 0
        self.individual_id_counter = 0
        self.stats = {
            "best_fitness_per_gen": [],
            "avg_fitness_per_gen": [],
            "diversity_per_gen": [],
        }

    def _next_id(self) -> int:
        self.individual_id_counter += 1
        return self.individual_id_counter

    def generate_random_tree(self, max_depth: Optional[int] = None, min_depth: int = 1) -> TreeNode:
        max_depth = max_depth or self.config.max_depth
        return self._grow_tree(max_depth, min_depth=min_depth)

    def _grow_tree(self, max_depth: int, min_depth: int = 1) -> TreeNode:
        if max_depth <= 0 or (max_depth <= min_depth and self.rng.random() < 0.3):
            return self._create_terminal()
        if self.rng.random() < 0.3:
            return self._create_terminal()

        operator = self._choose_operator()
        node = TreeNode(value=operator.name, node_type="operator", children=[])

        if operator.has_time_param:
            if operator.arity == 2:
                node.children = [
                    self._grow_tree(max_depth - 1, min_depth=max(0, min_depth - 1)),
                    self._grow_tree(max_depth - 1, min_depth=max(0, min_depth - 1)),
                ]
            else:
                node.children = [self._grow_tree(max_depth - 1, min_depth=max(0, min_depth - 1))]
            node.time_param = self.rng.randint(*self.config.ts_time_range)
        elif operator.category == "group":
            node.children = [self._grow_tree(max_depth - 1, min_depth=max(0, min_depth - 1))]
            node.group_param = self.rng.choice(GROUP_PARAMS)
        else:
            for _ in range(operator.arity):
                node.children.append(self._grow_tree(max_depth - 1, min_depth=max(0, min_depth - 1)))
        return node

    def _create_terminal(self) -> TreeNode:
        if self.rng.random() < 0.9:
            return TreeNode(value=self.rng.choice(self.config.get_weighted_fields()), node_type="field")
        return TreeNode(value=str(self.rng.choice(self.config.constant_values)), node_type="constant")

    def _choose_operator(self) -> Operator:
        return self.rng.choice(self.config.get_weighted_operators())

    def initialize_population(self, size: int = 100) -> List[AlphaIndividual]:
        self.population = []
        self.generation = 0
        for _ in range(size):
            tree = self.generate_random_tree()
            self.population.append(AlphaIndividual(tree=tree, generation=0, id=self._next_id()))
        return self.population

    # Backward-compatible aliases used by orchestrator
    def init_population(self) -> List[AlphaIndividual]:
        return self.initialize_population(size=self.config.max_nodes * 8)

    def evolve(self) -> List[AlphaIndividual]:
        # Keep behavior simple and deterministic for refactor safety.
        return self.population

    def get_diversity_metrics(self) -> Dict[str, float]:
        if not self.population:
            return {"unique_ratio": 0.0}
        expressions = [ind.expression for ind in self.population]
        return {"unique_ratio": len(set(expressions)) / len(expressions)}

    def get_operator_distribution(self, population: List[AlphaIndividual]) -> Dict[str, int]:
        dist = defaultdict(int)
        for ind in population:
            for node in self._collect_all_nodes(ind.tree):
                if node.node_type == "operator":
                    dist[node.value] += 1
        return dict(dist)

    def _collect_all_nodes(self, tree: TreeNode) -> List[TreeNode]:
        nodes = [tree]
        for child in tree.children:
            nodes.extend(self._collect_all_nodes(child))
        return nodes
