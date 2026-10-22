from __future__ import annotations

from typing import Any


class SubmissionPlanner:
    """Minimal planner gate for Phase 4 submission checks.

    Acceptance behavior:
    - an alpha is only submittable with an explicit confirm token
    - failed checks are rejected before a submission attempt
    - platform submission checks are invoked before listing as ready
    """

    def __init__(self, check_submission: Any | None = None):
        self.check_submission = check_submission or self._check_submission

    def _check_submission(self, alpha: dict[str, Any]) -> bool:
        checks = alpha.get("checks", [])
        return isinstance(checks, list) and all(bool(check.get("passed", False)) for check in checks)

    def can_submit(self, alpha: dict[str, Any], *, confirm_token: str | None = None) -> bool:
        if not confirm_token:
            return False
        if not isinstance(alpha, dict):
            return False
        if not self._check_submission(alpha):
            return False
        return bool(self.check_submission(alpha))

    def ready_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [candidate for candidate in candidates if self.can_submit(candidate, confirm_token="confirmed")]

    def submit(self, alpha: dict[str, Any], *, confirm_token: str | None = None) -> dict[str, Any]:
        if not self.can_submit(alpha, confirm_token=confirm_token):
            return {
                "submitted": False,
                "reason": "missing_confirmation" if not confirm_token else "alpha_failed_checks",
                "alpha_id": alpha.get("id"),
            }
        return {"submitted": True, "alpha_id": alpha.get("id"), "status": "ready"}


class AlphaDetail:
    def __init__(self, alpha: dict[str, Any]):
        self.alpha = alpha or {}

    @classmethod
    def from_alpha(cls, alpha: dict[str, Any]) -> "AlphaDetail":
        return cls(alpha)

    def payload(self) -> dict[str, Any]:
        return {
            "id": self.alpha.get("id"),
            "expression": self.alpha.get("expression"),
            "settings": self.alpha.get("settings", {}),
            "dataset": self.alpha.get("dataset"),
            "hypothesis": self.alpha.get("hypothesis"),
            "lineage": self.alpha.get("lineage", {}),
            "checks": self.alpha.get("checks", []),
        }
