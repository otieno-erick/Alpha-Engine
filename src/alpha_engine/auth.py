from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SyncService:
    region: str = "ALL"
    field_count: int = 0
    fields: List[str] = None

    def __post_init__(self):
        if self.fields is None:
            self.fields = []

    def update(self, fields: List[str], region: str = "ALL") -> None:
        self.fields = fields
        self.region = region
        self.field_count = len(fields)

    def summary(self) -> Dict[str, Any]:
        return {"region": self.region, "field_count": self.field_count}


DEFAULT_SYNC_SERVICE = SyncService()
