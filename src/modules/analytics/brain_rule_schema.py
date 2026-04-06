from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


# Tokenizer should be consistent with the project's existing correlation logic.
# See: `src/modules/validator/filter.py::_tokenize_expression`
EXPR_TOKEN_RE = re.compile(r"[a-z_]+|\d+\.?\d*|[+\-*/(),]")


def tokenize_expression(expression: str) -> List[str]:
    """
    Tokenize an alpha expression into coarse tokens.

    This intentionally mirrors the regex used for correlation filtering so that
    ML models can reuse the same "language" of tokens.
    """

    if not expression:
        return []
    tokens = EXPR_TOKEN_RE.findall(expression.lower())
    # Normalize: remove parentheses / commas only; keep operators/field/const/number tokens.
    return [t for t in tokens if t not in ("(", ")", ",")]


@dataclass(frozen=True)
class BrainCheck:
    name: str
    result: str  # PASS / FAIL / PENDING / ...
    limit: Optional[float] = None
    value: Optional[float] = None
    competitions: Optional[List[Dict[str, Any]]] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BrainCheck":
        # Typical payload from BRAIN: {"name":"LOW_SHARPE","result":"FAIL","limit":1.25,"value":0.93,...}
        name = str(d.get("name") or d.get("test") or "")
        result = str(d.get("result") or d.get("status") or "")
        limit = d.get("limit")
        value = d.get("value")
        competitions = d.get("competitions")
        return BrainCheck(
            name=name,
            result=result,
            limit=float(limit) if isinstance(limit, (int, float, str)) and str(limit).strip() != "" else None,
            value=float(value) if isinstance(value, (int, float, str)) and str(value).strip() != "" else None,
            competitions=competitions if isinstance(competitions, list) else None,
            raw=dict(d),
        )


@dataclass
class BrainRuleOutcome:
    """
    One alpha's IS-testing checks normalized to a structured format.
    """

    alpha_id: str
    expression: str

    sharpe: Optional[float] = None
    fitness: Optional[float] = None
    turnover: Optional[float] = None
    returns_pct: Optional[float] = None
    # Simulation settings used for this alpha (for training context)
    instrument_type: Optional[str] = None
    region: Optional[str] = None
    universe: Optional[str] = None
    delay: Optional[int] = None
    decay: Optional[int] = None
    truncation: Optional[float] = None
    neutralization: Optional[str] = None
    pasteurization: Optional[str] = None
    nan_handling: Optional[str] = None
    unit_handling: Optional[str] = None
    language: Optional[str] = None
    test_period: Optional[str] = None

    checks: List[BrainCheck] = field(default_factory=list)

    is_submitted: bool = False
    required_checks_passed: bool = False
    is_good_for_submit: bool = False

    def checks_by_name(self) -> Dict[str, BrainCheck]:
        return {c.name: c for c in self.checks if c.name}


DEFAULT_REQUIRED_CHECK_NAMES: Set[str] = {
    # From the BRAIN IS Testing UI examples you shared.
    "LOW_SHARPE",
    "LOW_FITNESS",
    "LOW_TURNOVER",
    "HIGH_TURNOVER",
    "CONCENTRATED_WEIGHT",
    "LOW_SUB_UNIVERSE_SHARPE",
    "MATCHES_COMPETITION",
    # Correlation/pending checks exist in some payloads; we do not treat them as hard required by default.
}


def is_alpha_good_for_submit(
    checks: Iterable[BrainCheck],
    required_check_names: Set[str] = DEFAULT_REQUIRED_CHECK_NAMES,
) -> Tuple[bool, bool]:
    """
    Returns:
      (required_checks_passed, is_good_for_submit)
    """

    by_name = {c.name: c for c in checks if c.name}
    if not required_check_names:
        required_passed = True
    else:
        required_passed = all(
            (by_name.get(name) is not None and by_name[name].result == "PASS") for name in required_check_names
        )

    # For safety: any FAIL among required checks makes it not good.
    any_required_fail = any(
        (by_name.get(name) is not None and by_name[name].result == "FAIL") for name in required_check_names
    )
    is_good = required_passed and not any_required_fail
    return required_passed, is_good


def normalize_checks(raw_checks: Any) -> List[BrainCheck]:
    if not raw_checks:
        return []
    if not isinstance(raw_checks, list):
        return []
    return [BrainCheck.from_dict(c) for c in raw_checks if isinstance(c, dict)]


def extract_primary_expression(payload: Dict[str, Any]) -> str:
    """
    Extract the expression code as stored by BRAIN simulation result JSON.
    """

    regular = payload.get("regular") if isinstance(payload, dict) else None
    if isinstance(regular, dict):
        # Typical: {"code": "...", ...}
        code = regular.get("code")
        if isinstance(code, str):
            return code
    # Fallbacks
    if isinstance(payload.get("regular"), str):
        return payload["regular"]
    return ""

