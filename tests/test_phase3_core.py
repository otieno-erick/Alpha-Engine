from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Hypothesis:
    dataset: str
    rationale: str
    expression: str
    prompt_version: str


@dataclass
class LineageRecord:
    parent: Optional[str]
    settings: Dict[str, Any]
    result: Dict[str, Any]
    failure_reason: Optional[str]
    prompt_version: str


class CreationLoop:
    def __init__(self):
        self.hypotheses: List[Hypothesis] = []
        self.lineage: List[LineageRecord] = []

    def select_datasets(self, datasets: List[str], *, user_filters: Optional[Dict[str, Any]] = None) -> List[str]:
        if not datasets:
            return ["USA_D0_TOP", "ASI_D1_TOP"]
        return datasets

    def generate_hypotheses(self, datasets: List[str], *, prompt_version: str = "alpha_generation") -> List[Hypothesis]:
        items = []
        for dataset in datasets:
            items.append(
                Hypothesis(
                    dataset=dataset,
                    rationale=f"Economic signal in {dataset} and align with the userâ€™s factor exposure.",
                    expression=f"alpha_{dataset.lower()}_signal",
                    prompt_version=prompt_version,
                )
            )
        self.hypotheses.extend(items)
        return items

    def generate_expressions(self, hypotheses: List[Hypothesis]) -> List[Dict[str, Any]]:
        expressions = []
        for h in hypotheses:
            expressions.append({"dataset": h.dataset, "expression": h.expression, "hypothesis": h.rationale, "prompt_version": h.prompt_version})
        return expressions

    def run_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        selected = self.select_datasets(config.get("datasets", []), user_filters=config.get("user_filters"))
        hypotheses = self.generate_hypotheses(selected, prompt_version=config.get("prompt_version", "alpha_generation"))
        expressions = self.generate_expressions(hypotheses)
        result = {
            "selected_datasets": selected,
            "count": len(expressions),
            "expressions": expressions,
            "status": "generated",
        }
        self.lineage.append(
            LineageRecord(
                parent=config.get("parent"),
                settings=config,
                result=result,
                failure_reason=config.get("failure_reason"),
                prompt_version=config.get("prompt_version", "alpha_generation"),
            )
        )
        return result


DEFAULT_CREATION_LOOP = CreationLoop()

