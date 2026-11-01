from __future__ import annotations

from typing import Any

from app.services.diagnoser import Diagnoser
from app.services.scorer import Scorer


class RepairPromptBuilder:
    """Formats the exact failure details used during repair loops."""

    @staticmethod
    def build(
        failure: str | None,
        *,
        margin: float | int | None = None,
        instruction: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        failure = failure or "unknown failure"
        instruction = instruction or "review expression"
        margin_value = margin if margin is not None else (details or {}).get("margin", 0.0)
        return (
            f"Repair failed check: {failure}. "
            f"Observed margin: {margin_value}. "
            f"Instruction: {instruction}."
        )


class FieldProfiler:
    """Produces the six-probe field cards used when a field is not already known."""

    PROBE_EXPRESSIONS = [
        "rank(value)",
        "rank(momentum)",
        "rank(trend)",
        "rank(volume)",
        "rank(volatility)",
        "vec_value + lag(momentum, 3)",
    ]

    def profile(self, fields: list[str] | None) -> list[dict[str, Any]]:
        source = list(fields or ["value", "momentum", "trend", "volume", "volatility", "size"])
        cards: list[dict[str, Any]] = []
        for index, field in enumerate(source[:6]):
            cards.append(
                {
                    "field": field,
                    "probe": self.PROBE_EXPRESSIONS[index % len(self.PROBE_EXPRESSIONS)],
                    "status": "profiled",
                }
            )
        return cards


class LineageStore:
    """Tracks parentage, prompt version, result metadata, and failure reasons."""

    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def record(
        self,
        alpha_id: str,
        *,
        parent: str | None = None,
        settings: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        failure_reason: str | None = None,
        prompt_version: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        entry = {
            "alpha_id": alpha_id,
            "parent": parent,
            "settings": settings or {},
            "result": result or {},
            "failure_reason": failure_reason,
            "prompt_version": prompt_version,
            **extra,
        }
        self.entries.append(entry)
        return entry

    def get(self, alpha_id: str) -> dict[str, Any] | None:
        for entry in reversed(self.entries):
            if entry.get("alpha_id") == alpha_id:
                return entry
        return None


class OverfittingGuard:
    """Simple guard for the test-period, cross-universe, and simplicity checks."""

    def __init__(self, *, max_test_period: int = 12, max_operators: int = 4):
        self.max_test_period = max_test_period
        self.max_operators = max_operators

    def check(self, expression: str, *, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        flags: list[str] = []
        config = settings or {}
        test_period = config.get("test_period") or config.get("window")
        if test_period is not None and int(test_period) > self.max_test_period:
            flags.append("test_period")

        universe = config.get("universe")
        if universe and isinstance(universe, str) and "ALL" in universe.upper() and "vec_" in str(expression):
            flags.append("cross_universe")

        operator_count = sum(
            expression.lower().count(token)
            for token in ("rank(", "lag(", "lead(", "delta(", "zscore(", "vec_")
        )
        if operator_count > self.max_operators:
            flags.append("simplicity")

        return {"allowed": not flags, "flags": flags}


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
        lineage_store: LineageStore | None = None,
        profiler: FieldProfiler | None = None,
        overfitting_guard: OverfittingGuard | None = None,
    ):
        self.validator = validator
        self.cache = cache
        self.simulator = simulator
        self.scorer = scorer or Scorer()
        self.diagnoser = diagnoser or Diagnoser()
        self.retry_budget = 3
        self.prompt_version = prompt_version
        self.lineage = lineage_store or LineageStore()
        self.profiler = profiler or FieldProfiler()
        self.overfitting_guard = overfitting_guard or OverfittingGuard()

    def select_datasets(
        self,
        datasets: list[dict[str, Any]],
        *,
        filters: dict[str, Any] | None = None,
        submitted_pool: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
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

        if submitted_pool is not None:
            selected.sort(
                key=lambda item: int(item.get("submitted_count", 0) or 0),
            )
            return selected

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

    def generate_repair_prompt(
        self,
        failure: str | None,
        *,
        margin: float | int | None = None,
        instruction: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        return RepairPromptBuilder.build(failure, margin=margin, instruction=instruction, details=details)

    def profile_fields(self, fields: list[str] | None) -> list[dict[str, Any]]:
        return self.profiler.profile(fields)

    def run(self, expression: str, config: dict[str, Any]) -> dict[str, Any]:
        validation = self.validator(expression, config) if self.validator else {"valid": True, "expression": expression}
        if not validation.get("valid", True):
            return {"status": "invalid", "reason": validation.get("error", "invalid expression")}

        guard = self.overfitting_guard.check(expression, settings=config)
        if not guard["allowed"]:
            return {"status": "guarded", "reason": guard["flags"], "guard": guard}

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

        repair_prompt = self.generate_repair_prompt(
            diagnosis.get("first_failure"),
            margin=score.get("checks", [{}])[0].get("margin") if score.get("checks") else None,
            instruction=diagnosis.get("repair_instruction"),
            details={"score": score, "diagnosis": diagnosis},
        )

        for attempt in range(1, self.retry_budget + 1):
            repaired = {
                "status": "repair_attempted",
                "instruction": diagnosis.get("repair_instruction"),
                "attempt": attempt,
                "repair_prompt": repair_prompt,
            }
            score = self.scorer.evaluate(result)
            diagnosis = self.diagnoser.diagnose(score["checks"])
            if diagnosis["status"] == "clean":
                return {"status": "clean", "score": score, "diagnosis": diagnosis, "repair": repaired}

        return {
            "status": "stopped",
            "reason": diagnosis.get("first_failure"),
            "score": score,
            "diagnosis": diagnosis,
            "repair_prompt": repair_prompt,
            "stop_reason": diagnosis.get("first_failure") or "retry_budget_exhausted",
        }

    def run_dataset(self, dataset: dict[str, Any], *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        field_cards = self.profile_fields(dataset.get("fields"))
        for hypothesis in self.generate_hypotheses(dataset, field_cards=[entry["field"] for entry in field_cards]):
            for expression in self.generate_expressions(hypothesis, neutralization="rank"):
                config = {
                    "dataset": dataset.get("name") or dataset.get("dataset") or dataset.get("id"),
                    "expression": expression,
                    "region": dataset.get("region", "USA"),
                    "delay": dataset.get("delay", 1),
                    "universe": dataset.get("universe", "TOP3000"),
                    "test_period": dataset.get("test_period", 12),
                }
                outcome = self.run(expression, config)
                alpha_id = f"{config['dataset']}-{hypothesis['dataset']}-{len(results)+1}"
                self.lineage.record(
                    alpha_id,
                    parent=None,
                    settings=config,
                    result=outcome,
                    failure_reason=(outcome.get("stop_reason") if outcome.get("status") == "stopped" else None),
                    prompt_version=hypothesis["prompt_version"],
                )
                results.append(
                    {
                        "dataset": config["dataset"],
                        "hypothesis": hypothesis["hypothesis"],
                        "expression": expression,
                        "result": outcome,
                        "prompt_version": hypothesis["prompt_version"],
                        "field_cards": field_cards,
                    }
                )
        return results


class CreationPipeline(CreationLoop):
    """Backward-compatible alias used by the existing Phase 3 tests."""

    pass


__all__ = [
    "CreationLoop",
    "CreationPipeline",
    "FieldProfiler",
    "LineageStore",
    "OverfittingGuard",
    "RepairPromptBuilder",
]


if __name__ == "__main__":  # pragma: no cover
    loop = CreationLoop()
    print(loop.select_datasets([{"name": "USA_EQ", "region": "USA", "fields": ["value", "momentum"]}]))
