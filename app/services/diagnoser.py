from __future__ import annotations

from typing import Any


class Diagnoser:
    def __init__(self, rules: dict[str, Any] | None = None):
        self.rules = rules or {}
        self.order = [
            "max_weight",
            "turnover",
            "is_ladder",
            "sharpe",
            "correlation",
        ]
        self.map = {
            "max_weight": "weight/coverage",
            "turnover": "turnover under 30%",
            "is_ladder": "IS Ladder",
            "sharpe": "Sharpe",
            "correlation": "correlation structural change",
        }

    def diagnose(self, checks: list[dict[str, Any]]) -> dict[str, Any]:
        failed = [check for check in checks if not check.get("passed", False)]
        if not failed:
            return {"status": "clean", "first_failure": None, "repair_instruction": None, "repair_type": None}

        order_index = {name: idx for idx, name in enumerate(self.order)}
        first = min(failed, key=lambda item: order_index.get(item.get("id"), 999))
        repair_instruction = self.map.get(first["id"], "review expression")
        repair_type = "structural_change" if first["id"] == "correlation" else "repair"

        return {
            "status": "failed",
            "first_failure": first["id"],
            "repair_instruction": repair_instruction,
            "repair_type": repair_type,
        }
