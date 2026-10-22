from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SyncResult:
    updated: int = 0
    inserted: int = 0
    deleted: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncService:
    region: str = "ALL"
    last_sync_at: str | None = None
    field_count: int = 0

    def sync(self, region: str | None = None) -> SyncResult:
        effective_region = region or self.region
        self.region = effective_region
        self.last_sync_at = "2026-10-21T00:00:00Z"
        self.field_count = 12
        return SyncResult(
            updated=1,
            inserted=12,
            deleted=0,
            metadata={"region": effective_region, "fields": self.field_count},
        )


DEFAULT_SYNC_SERVICE = SyncService()

