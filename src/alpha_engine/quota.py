from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class QuotaLedger:
    reserve: int = 5
    remaining_quota: int = 100
    used_today: int = 0
    by_source: Dict[str, int] = field(default_factory=lambda: {
        "LLM": 0,
        "Evolution": 0,
        "PowerPool": 0,
        "ATOM": 0,
        "Template": 0,
        "Sampler": 0,
        "CorrBreaker": 0,
    })

    def can_spend(self, requested: int = 1) -> bool:
        return (self.remaining_quota - requested) >= self.reserve

    def spend(self, source: str, requested: int = 1) -> bool:
        if not self.can_spend(requested):
            return False
        self.used_today += requested
        self.remaining_quota -= requested
        self.by_source[source] = self.by_source.get(source, 0) + requested
        return True

    def summary(self) -> Dict[str, Any]:
        return {
            "reserve": self.reserve,
            "remaining_quota": self.remaining_quota,
            "used_today": self.used_today,
            "by_source": self.by_source,
        }


DEFAULT_QUOTA_LEDGER = QuotaLedger()

