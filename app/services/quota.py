from __future__ import annotations

from typing import Any

from app.services.rules import get_rule


class QuotaGuard:
    def __init__(self, rules: dict[str, Any]):
        self.rules = rules
        self.reserve = int(rules.get("quota.reserve", {}).get("value", 10))
        self.remaining_today = 100

    def remaining(self) -> int:
        return self.remaining_today

    def set_remaining(self, value: int) -> None:
        self.remaining_today = max(0, value)

    def can_send(self, headers: dict | None = None, requested: int = 1) -> bool:
        remaining = int((headers or {}).get("X-Ratelimit-Remaining", self.remaining_today))
        return remaining > self.reserve + requested - 1

    def enforce(self, headers: dict | None = None, requested: int = 1) -> bool:
        return self.can_send(headers=headers, requested=requested)

