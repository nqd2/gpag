"""
Alpha Expression Grammar for WorldQuant BRAIN FastExpression syntax.
Defines the building blocks: operators, data fields, and groupings.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path

# Price-based fields
PRICE_FIELDS = [
    "close",
    "open",
    "high",
    "low",
    "vwap",
    "returns",
    "cap",
    "volume",
    "turnover",
    "adv20",
    "adv40",
    "adv60",
    "amount",
    "shares",
    "openinterest",
]

FUNDAMENTAL_FIELDS = [
    "market_cap",
    "pe",
    "pb",
    "ps",
    "pcf",
    "dividend_yield",
    "roe",
    "roa",
    "revenue",
    "net_income",
    "eps",
    "book_value",
    "total_assets",
    "total_liabilities",
    "cash",
    "debt",
    "gross_profit",
    "operating_income",
    "ebitda",
]

TECHNICAL_FIELDS = [
    "momentum_5d",
    "momentum_10d",
    "momentum_20d",
    "momentum_60d",
    "volatility_5d",
    "volatility_10d",
    "volatility_20d",
    "volatility_60d",
    "skewness_20d",
    "kurtosis_20d",
    "rsi_14",
    "macd",
    "bb_upper",
    "bb_lower",
]

ALTERNATIVE_FIELDS = [
    "sentiment_score",
    "news_volume",
    "analyst_rating",
    "earnings_surprise",
    "revision_up",
    "revision_down",
]

ALL_FIELDS = PRICE_FIELDS + FUNDAMENTAL_FIELDS + TECHNICAL_FIELDS + ALTERNATIVE_FIELDS


@dataclass
class Operator:
    name: str
    arity: int
    min_args: int = 0
    max_args: int = 0
    has_time_param: bool = False
    time_param_range: tuple = (2, 60)
    category: str = "general"
    description: str = ""


def _extract_operator_tokens(raw_name: str) -> List[str]:
    tokens: List[str] = []
    for part in raw_name.split(","):
        token = part.strip()
        if not token:
            continue
        if "(" in token:
            fn_name = token.split("(", 1)[0].strip()
            if fn_name:
                tokens.append(fn_name)
            continue
        if any(sym in token for sym in ("+", "-", "*", "/", "<", ">", "=", "!")):
            continue
        tokens.append(token)
    return tokens


def _load_documented_operator_names() -> set:
    operators_path = Path(__file__).resolve().parents[3] / "docs" / "operators.json"
    if not operators_path.exists():
        return set()
    try:
        data = json.loads(operators_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    names = set()
    for item in data:
        raw_name = item.get("Operator Name", "")
        for token in _extract_operator_tokens(raw_name):
            names.add(token)
    return names


DOCUMENTED_OPERATOR_NAMES = _load_documented_operator_names()
OPERATOR_NAME_ALIASES = {
    "ts_stddev": "ts_std_dev",
    "decay_linear": "ts_decay_linear",
    "neg": "reverse",
}


def _canonical_operator_name(name: str) -> str:
    return OPERATOR_NAME_ALIASES.get(name, name)


def _filter_to_documented(operators: List[Operator]) -> List[Operator]:
    if not DOCUMENTED_OPERATOR_NAMES:
        return operators
    filtered = [op for op in operators if _canonical_operator_name(op.name) in DOCUMENTED_OPERATOR_NAMES]
    return filtered or operators


UNARY_OPERATORS = _filter_to_documented(
    [
        Operator("rank", 1, category="cross_sectional"),
        Operator("zscore", 1, category="cross_sectional"),
        Operator("scale", 1, category="cross_sectional"),
        Operator("normalize", 1, category="cross_sectional"),
        Operator("abs", 1, category="math"),
        Operator("sign", 1, category="math"),
        Operator("log", 1, category="math"),
        Operator("sqrt", 1, category="math"),
        Operator("reverse", 1, category="math"),
    ]
)

TS_OPERATORS = _filter_to_documented(
    [
        Operator("ts_mean", 1, has_time_param=True, category="time_series"),
        Operator("ts_std_dev", 1, has_time_param=True, category="time_series"),
        Operator("ts_sum", 1, has_time_param=True, category="time_series"),
        Operator("ts_min", 1, has_time_param=True, category="time_series"),
        Operator("ts_max", 1, has_time_param=True, category="time_series"),
        Operator("ts_rank", 1, has_time_param=True, category="time_series"),
        Operator("ts_delta", 1, has_time_param=True, category="time_series"),
        Operator("ts_delay", 1, has_time_param=True, category="time_series"),
        Operator("ts_arg_max", 1, has_time_param=True, category="time_series"),
        Operator("ts_arg_min", 1, has_time_param=True, category="time_series"),
        Operator("ts_decay_linear", 1, has_time_param=True, category="smoothing"),
    ]
)

BINARY_OPERATORS = _filter_to_documented(
    [
        Operator("+", 2, category="arithmetic"),
        Operator("-", 2, category="arithmetic"),
        Operator("*", 2, category="arithmetic"),
        Operator("/", 2, category="arithmetic"),
        Operator("max", 2, category="arithmetic"),
        Operator("min", 2, category="arithmetic"),
    ]
)

BINARY_TS_OPERATORS = _filter_to_documented(
    [
        Operator("ts_corr", 2, has_time_param=True, category="time_series", time_param_range=(5, 60)),
        Operator(
            "ts_covariance",
            2,
            has_time_param=True,
            category="time_series",
            time_param_range=(5, 60),
        ),
    ]
)

GROUP_OPERATORS = _filter_to_documented(
    [
        Operator("group_rank", 1, category="group"),
        Operator("group_zscore", 1, category="group"),
        Operator("group_mean", 1, category="group"),
        Operator("group_neutralize", 1, category="group"),
        Operator("group_scale", 1, category="group"),
    ]
)

GROUP_PARAMS = ["industry", "sector", "subindustry", "market_cap_bucket", "country"]


@dataclass
class TreeNode:
    value: str
    node_type: str
    children: List["TreeNode"] = field(default_factory=list)
    time_param: Optional[int] = None
    group_param: Optional[str] = None

    def to_string(self) -> str:
        if self.node_type in ("field", "constant"):
            return self.value
        if self.node_type == "operator":
            if self.time_param is not None:
                if len(self.children) == 2:
                    return (
                        f"{self.value}({self.children[0].to_string()}, "
                        f"{self.children[1].to_string()}, {self.time_param})"
                    )
                return f"{self.value}({self.children[0].to_string()}, {self.time_param})"
            if self.group_param is not None:
                return f"{self.value}({self.children[0].to_string()}, {self.group_param})"
            if len(self.children) == 1:
                return f"{self.value}({self.children[0].to_string()})"
            if len(self.children) == 2:
                return f"{self.value}({self.children[0].to_string()}, {self.children[1].to_string()})"
        return self.value

    def depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(child.depth() for child in self.children)

    def node_count(self) -> int:
        return 1 + sum(child.node_count() for child in self.children)

    def copy(self) -> "TreeNode":
        import copy

        return copy.deepcopy(self)


@dataclass
class GrammarConfig:
    price_field_weight: float = 0.50
    fundamental_field_weight: float = 0.25
    technical_field_weight: float = 0.20
    alternative_field_weight: float = 0.05
    unary_weight: float = 0.30
    ts_weight: float = 0.40
    binary_weight: float = 0.20
    group_weight: float = 0.10
    max_depth: int = 5
    max_nodes: int = 25
    min_depth: int = 2
    ts_time_range: tuple = (3, 20)
    ts_time_range_extended: tuple = (10, 60)
    constant_values: List[float] = field(default_factory=lambda: [0.5, 1.0, 2.0, -1.0, 0.1, 0.01])

    def get_weighted_fields(self) -> List[str]:
        fields: List[str] = []
        fields.extend(PRICE_FIELDS * int(self.price_field_weight * 100))
        fields.extend(FUNDAMENTAL_FIELDS * int(self.fundamental_field_weight * 100))
        fields.extend(TECHNICAL_FIELDS * int(self.technical_field_weight * 100))
        fields.extend(ALTERNATIVE_FIELDS * int(self.alternative_field_weight * 100))
        return fields if fields else PRICE_FIELDS

    def get_weighted_operators(self) -> List[Operator]:
        operators: List[Operator] = []
        operators.extend(UNARY_OPERATORS * int(self.unary_weight * 100))
        operators.extend(TS_OPERATORS * int(self.ts_weight * 100))
        operators.extend(BINARY_OPERATORS * int(self.binary_weight * 100))
        operators.extend(GROUP_OPERATORS * int(self.group_weight * 100))
        return operators if operators else UNARY_OPERATORS + TS_OPERATORS
