from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Dict, Optional


@dataclass
class HashCache:
    entries: Dict[str, str] = field(default_factory=dict)
    prune_days: int = 90

    @staticmethod
    def compute_hash(config: Dict[str, Any]) -> str:
        payload = json.dumps(config, sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()

    def get(self, config: Dict[str, Any]) -> Optional[str]:
        key = self.compute_hash(config)
        return self.entries.get(key)

    def set(self, config: Dict[str, Any], value: str) -> str:
        key = self.compute_hash(config)
        if key not in self.entries:
            self.entries[key] = value
        return key

    def has_duplicate(self, config: Dict[str, Any]) -> bool:
        return self.get(config) is not None

    def prune(self, cutoff_days: Optional[int] = None) -> int:
        self.prune_days = cutoff_days or self.prune_days
        return 0


DEFAULT_HASH_CACHE = HashCache()

