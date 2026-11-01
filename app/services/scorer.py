from __future__ import annotations

from typing import Any


class Scorer:
    def __init__(self, rules: dict[str, Any] | None = None):
        self.rules = rules or {}

    def _rule(self, key: str, default: Any = None) -> Any:
        return self.rules.get(key, {}).get("value", default)

    def evaluate(self, results: dict[str, Any]) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def add_check(check_id: str, value: float, threshold: float, *, applicable: bool = True):
            margin = round(float(value) - float(threshold), 2)
            checks.append(
                {
                    "id": check_id,
                    "value": value,
                    "threshold": threshold,
                    "margin": margin,
                    "passed": applicable and value >= threshold,
                    "applicable": applicable,
                }
            )

        sub_universe = float(results.get("sub_universe", 0.0))
        threshold = float(self._rule("sub_universe_cutoff", 1.18))
        add_check("sub_universe", sub_universe, threshold)

        sharpe = float(results.get("sharpe", 0.0))
        add_check("sharpe", sharpe, float(self._rule("consultant_d1_sharpe", 1.58)))

        turnover = float(results.get("turnover", 0.0))
        ladder_value = float(results.get("is_ladder", 0.0))
        if turnover < 0.30:
            ladder_value *= float(self._rule("is_ladder_discount", 0.85))
        add_check("is_ladder", ladder_value, float(self._rule("is_ladder_cutoff", 1.59)))

        max_weight = float(results.get("max_weight", 0.0))
        add_check("max_weight", max_weight, float(self._rule("max_weight_fail_pct", 10.0)))

        clean = all(check["passed"] for check in checks)
        failed = [check for check in checks if not check["passed"]]
        return {
            "clean": clean,
            "checks": checks,
            "first_failure": failed[0]["id"] if failed else None,
        }
