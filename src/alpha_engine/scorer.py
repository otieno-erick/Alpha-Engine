from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RepairInstruction:
    failure: str
    action: str
    priority: int


class Diagnoser:
    def __init__(self):
        self.mapping = {
            "turnover_floor": RepairInstruction("turnover_floor", "increase turnover or reduce turnover floor risk", 1),
            "is_ladder": RepairInstruction("is_ladder", "adjust IS ladder and turnover assumptions", 2),
            "correlation": RepairInstruction("correlation", "change dataset, region, or delta structure", 3),
            "fitness": RepairInstruction("fitness", "rework operator settings and weights", 4),
        }

    def diagnose(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for check in checks:
            if not check.get("passed", True):
                failure = check.get("name")
                instruction = self.mapping.get(failure, RepairInstruction(failure, "review configuration", 999))
                return {
                    "first_failure": failure,
                    "action": instruction.action,
                    "priority": instruction.priority,
                    "margin": check.get("margin", 0.0),
                }
        return {"first_failure": None, "action": "no repair required", "priority": 0, "margin": 0.0}


DEFAULT_DIAGNOSER = Diagnoser()

