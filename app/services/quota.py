from __future__ import annotations

from typing import Any


class QuotaGuard:
    def __init__(self, rules: dict[str, Any] | None = None):
        self.rules = rules or {}
        reserve_rule = (self.rules.get("quota.reserve") or {})
        self.reserve = int(reserve_rule.get("value", 10))
        self.remaining_today = 100

    def remaining(self) -> int:
        return self.remaining_today

    def set_remaining(self, value: int) -> None:
        self.remaining_today = max(0, int(value))

    def can_send(self, headers: dict | None = None, requested: int = 1) -> bool:
        remaining = int((headers or {}).get("X-Ratelimit-Remaining", self.remaining_today))
        return remaining - requested >= self.reserve

    def enforce(self, headers: dict | None = None, requested: int = 1) -> bool:
        return self.can_send(headers=headers, requested=requested)
