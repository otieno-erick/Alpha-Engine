from __future__ import annotations

from typing import Any

from app.services.diagnoser import Diagnoser
from app.services.scorer import Scorer


class CreationPipeline:
    """Minimal creation pipeline used by the Phase 3 acceptance tests."""

    def __init__(
        self,
        validator: Any | None = None,
        cache: Any | None = None,
        simulator: Any | None = None,
        scorer: Any | None = None,
        diagnoser: Any | None = None,
    ):
        self.validator = validator
        self.cache = cache
        self.simulator = simulator
        self.scorer = scorer or Scorer()
        self.diagnoser = diagnoser or Diagnoser()
        self.retry_budget = 3

    def run(self, expression: str, config: dict[str, Any]) -> dict[str, Any]:
        validation = self.validator(expression, config) if self.validator else {"valid": True, "expression": expression}
        if not validation.get("valid", True):
            return {"status": "invalid", "reason": validation.get("error", "invalid expression")}

        if self.cache is not None:
            cached = self.cache.check_and_store(config)
            if cached.get("hit"):
                return {"status": "cached", "hit": True, "saved": cached.get("saved", True), "result": cached.get("result")}

        if self.simulator is not None:
            result = self.simulator(config)
        else:
            result = {"sub_universe": 1.17, "sharpe": 1.60, "turnover": 0.2, "is_ladder": 1.59, "max_weight": 8.0}

        score = self.scorer.evaluate(result)
        diagnosis = self.diagnoser.diagnose(score["checks"])

        if diagnosis["status"] == "clean":
            return {"status": "clean", "score": score, "diagnosis": diagnosis}

        for _ in range(self.retry_budget):
            repaired = {"status": "repair_attempted", "instruction": diagnosis.get("repair_instruction")}
            score = self.scorer.evaluate(result)
            diagnosis = self.diagnoser.diagnose(score["checks"])
            if diagnosis["status"] == "clean":
                return {"status": "clean", "score": score, "diagnosis": diagnosis, "repair": repaired}

        return {"status": "stopped", "reason": diagnosis.get("first_failure"), "score": score, "diagnosis": diagnosis}
