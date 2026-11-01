from __future__ import annotations

from typing import Any

from app.services.diagnoser import Diagnoser
from app.services.scorer import Scorer


class CreationLoop:
    """Minimal creation loop for the Phase 3 dataset -> hypothesis -> expression workflow."""

    def __init__(
        self,
        validator: Any | None = None,
        cache: Any | None = None,
        simulator: Any | None = None,
        scorer: Any | None = None,
        diagnoser: Any | None = None,
        *,
        prompt_version: str = "v1",
    ):
        self.validator = validator
        self.cache = cache
        self.simulator = simulator
        self.scorer = scorer or Scorer()
        self.diagnoser = diagnoser or Diagnoser()
        self.retry_budget = 3
        self.prompt_version = prompt_version

    def select_datasets(self, datasets: list[dict[str, Any]], *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        selected: list[dict[str, Any]] = []
        for dataset in datasets:
            if not isinstance(dataset, dict):
                continue
            if filters.get("region") and dataset.get("region") not in (None, filters["region"]):
                continue
            if filters.get("category") and dataset.get("category") != filters["category"]:
                continue
            selected.append(dict(dataset))
        return selected or [dict(item) for item in datasets]

    def generate_hypotheses(
        self,
        dataset: dict[str, Any],
        *,
        prompt_version: str | None = None,
        field_cards: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        dataset_name = str(dataset.get("name") or dataset.get("dataset") or dataset.get("id") or "unknown")
        cards = field_cards or list(dataset.get("fields", []) or ["value", "momentum", "trend"])
        version = prompt_version or self.prompt_version
        return [
            {
                "dataset": dataset_name,
                "hypothesis": f"Momentum continuation in {dataset_name}",
                "rationale": "Recent strength persists across the selected universe and region.",
                "field_cards": [str(card) for card in cards[:3]],
                "prompt_version": version,
            },
            {
                "dataset": dataset_name,
                "hypothesis": f"Mean reversion rotation in {dataset_name}",
                "rationale": "Short-term overreaction creates a favorable reversal signal.",
                "field_cards": [str(card) for card in cards[:3]],
                "prompt_version": version,
            },
        ]

    def generate_expressions(self, hypothesis: dict[str, Any], *, neutralization: str = "rank") -> list[str]:
        cards = hypothesis.get("field_cards") or ["value", "momentum", "trend"]
        primary = str(cards[0])
        secondary = str(cards[1]) if len(cards) > 1 else primary
        return [
            f"{neutralization}({primary}) + zscore({secondary})",
            f"vec_{primary} + lag({secondary}, 3)",
        ]

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

    def run_dataset(self, dataset: dict[str, Any], *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for hypothesis in self.generate_hypotheses(dataset, field_cards=list(dataset.get("fields", []) or ["value", "momentum", "trend"])):
            for expression in self.generate_expressions(hypothesis, neutralization="rank"):
                config = {
                    "dataset": dataset.get("name") or dataset.get("dataset") or dataset.get("id"),
                    "expression": expression,
                    "region": dataset.get("region", "USA"),
                    "delay": dataset.get("delay", 1),
                    "universe": dataset.get("universe", "TOP3000"),
                }
                outcome = self.run(expression, config)
                results.append(
                    {
                        "dataset": config["dataset"],
                        "hypothesis": hypothesis["hypothesis"],
                        "expression": expression,
                        "result": outcome,
                        "prompt_version": hypothesis["prompt_version"],
                    }
                )
        return results


class CreationPipeline(CreationLoop):
    """Backward-compatible alias used by the existing Phase 3 tests."""

    pass


__all__ = ["CreationLoop", "CreationPipeline"]


if __name__ == "__main__":  # pragma: no cover
    loop = CreationLoop()
    print(loop.select_datasets([{"name": "USA_EQ", "region": "USA", "fields": ["value", "momentum"]}]))
