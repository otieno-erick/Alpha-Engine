from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float
    margin: float
    threshold: float
    detail: str = ""


class Scorer:
    def score_alpha(self, result: Dict[str, Any]) -> List[CheckResult]:
        checks: List[CheckResult] = []
        turnover = float(result.get("turnover", 0.0))
        sharpe = float(result.get("sharpe", 0.0))
        correlation = float(result.get("correlation", 0.0))
        fitness = float(result.get("fitness", 0.0))

        checks.append(self._make_check(
            name="turnover_floor",
            passed=turnover >= 0.125,
            score=turnover,
            margin=turnover - 0.125,
            threshold=0.125,
            detail="turnover must be >= 12.5%"
        ))
        checks.append(self._make_check(
            name="is_ladder",
            passed=(sharpe >= 1.58) or (turnover < 0.30 and sharpe >= 1.58),
            score=sharpe,
            margin=sharpe - 1.58,
            threshold=1.58,
            detail="IS ladder threshold applies"
        ))
        checks.append(self._make_check(
            name="correlation",
            passed=correlation <= 0.70,
            score=correlation,
            margin=0.70 - correlation,
            threshold=0.70,
            detail="correlation threshold"
        ))
        checks.append(self._make_check(
            name="fitness",
            passed=fitness >= 0.0,
            score=fitness,
            margin=fitness,
            threshold=0.0,
            detail="fitness must be non-negative"
        ))
        return checks

    @staticmethod
    def _make_check(name: str, passed: bool, score: float, margin: float, threshold: float, detail: str) -> CheckResult:
        return CheckResult(name=name, passed=passed, score=score, margin=margin, threshold=threshold, detail=detail)

    def clean_alpha(self, result: Dict[str, Any]) -> bool:
        return all(check.passed for check in self.score_alpha(result))


DEFAULT_SCORER = Scorer()

