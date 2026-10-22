from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class Check:
    name: str
    passed_: bool
    margin: float = 0.0
    threshold: float = 0.0

    @property
    def passed(self) -> bool:
        return self.passed_


@dataclass
class Alpha:
    id: str
    expression: str
    dataset: str = "USA_D0_TOP"
    status: str = "unsubmitted"
    description: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    checks: Dict[str, Check] = field(default_factory=dict)

    @property
    def has_failed_checks(self) -> bool:
        return any(not check.passed for check in self.checks.values())

    @property
    def ready_to_submit(self) -> bool:
        return (not self.has_failed_checks) and len(self.description.strip()) >= 100

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "expression": self.expression,
            "dataset": self.dataset,
            "status": self.status,
            "description": self.description,
            "notes": self.notes,
            "tags": self.tags,
            "checks": {name: {"passed": c.passed, "margin": c.margin, "threshold": c.threshold} for name, c in self.checks.items()},
        }


class AlphaPopup:
    def __init__(self, alpha: Alpha):
        self.alpha = alpha

    def details(self) -> Dict[str, Any]:
        return {
            "id": self.alpha.id,
            "expression": self.alpha.expression,
            "dataset": self.alpha.dataset,
            "status": self.alpha.status,
            "description": self.alpha.description,
            "notes": self.alpha.notes,
            "tags": self.alpha.tags,
            "checks": {name: {"passed": c.passed, "margin": c.margin, "threshold": c.threshold} for name, c in self.alpha.checks.items()},
            "ready_to_submit": self.alpha.ready_to_submit,
        }


class PortfolioView:
    def __init__(self, alphas: Iterable[Alpha]):
        self.alphas = list(alphas)

    def summary(self) -> Dict[str, Any]:
        submitted = [a for a in self.alphas if a.status == "submitted"]
        return {
            "submitted_count": len(submitted),
            "unsubmitted_count": len(self.alphas) - len(submitted),
            "diversity_map": {dataset: sum(1 for a in self.alphas if a.dataset == dataset) for dataset in sorted({a.dataset for a in self.alphas})},
            "health_monitor": [a.id for a in self.alphas if a.has_failed_checks],
        }

    def degradation_flags(self) -> List[str]:
        return [a.id for a in self.alphas if a.has_failed_checks]


class SubmissionPlanner:
    def __init__(self, alphas: Optional[Iterable[Alpha]] = None):
        self.alphas = list(alphas) if alphas else []

    def ready_candidates(self) -> List[Alpha]:
        return [a for a in self.alphas if a.ready_to_submit]

    def zero_fail_candidates(self) -> List[Alpha]:
        return [a for a in self.alphas if not a.has_failed_checks]

    def description_valid(self, description: str, *, min_len: int = 100) -> bool:
        return len(description.strip()) >= min_len

    def submit(self, alpha_id: str, *, confirmation_token: str, description: Optional[str] = None) -> Dict[str, Any]:
        if not confirmation_token:
            raise ValueError("confirmation_token required")

        target = next((a for a in self.alphas if a.id == alpha_id), None)
        if target is None:
            raise KeyError(f"alpha not found: {alpha_id}")

        if description is not None:
            target.description = description

        if not target.ready_to_submit:
            return {"submitted": False, "alpha_id": alpha_id, "reason": "alpha is not ready to submit"}

        target.status = "submitted"
        return {"submitted": True, "alpha_id": alpha_id, "status": target.status}

    def checklist(self, alpha: Alpha) -> Dict[str, Any]:
        return {
            "zero_fail": not alpha.has_failed_checks,
            "description_length_ok": self.description_valid(alpha.description),
            "ready": alpha.ready_to_submit,
            "checks": {name: {"passed": c.passed, "margin": c.margin} for name, c in alpha.checks.items()},
        }


DEFAULT_SUBMISSION_PLANNER = SubmissionPlanner()

