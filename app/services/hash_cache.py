import hashlib
import json
from typing import Any


class HashCache:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self.saved_count = 0

    @staticmethod
    def _hash_config(config: dict) -> str:
        payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def check_and_store(self, config: dict) -> dict:
        key = self._hash_config(config)
        if key in self._store:
            self.saved_count += 1
            return {"hit": True, "saved": True, "cache_key": key, "result": self._store[key]}
        self._store[key] = {"status": "new", "config": config}
        return {"hit": False, "saved": False, "cache_key": key, "result": None}

    def reset(self):
        self._store.clear()
        self.saved_count = 0

