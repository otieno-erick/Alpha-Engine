from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


class HashCache:
    def __init__(self):
        self.entries: Dict[str, str] = {}

    def _key(self, config: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()

    def set(self, config: Dict[str, Any], value: str) -> str:
        key = self._key(config)
        if key not in self.entries:
            self.entries[key] = value
        return self.entries[key]

    def get(self, config: Dict[str, Any]) -> Optional[str]:
        return self.entries.get(self._key(config))

    def has_duplicate(self, config: Dict[str, Any]) -> bool:
        return self._key(config) in self.entries


DEFAULT_HASH_CACHE = HashCache()
