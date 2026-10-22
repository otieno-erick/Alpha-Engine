from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class QuotaLedger:
    reserve: int = 5
    remaining_quota: int = 10
    usage: Dict[str, int] = field(default_factory=dict)

    def can_spend(self, amount: int = 1) -> bool:
        return (self.remaining_quota - self.reserve) >= amount

    def spend(self, source: str, amount: int) -> bool:
        if not self.can_spend(amount):
            return False
        self.usage[source] = self.usage.get(source, 0) + amount
        self.remaining_quota -= amount
        return True

    def summary(self) -> Dict[str, Any]:
        return {"reserve": self.reserve, "remaining_quota": self.remaining_quota, "usage": self.usage}


DEFAULT_QUOTA_LEDGER = QuotaLedger()
