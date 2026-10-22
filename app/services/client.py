from __future__ import annotations

from typing import Any


class BrainClient:
    def __init__(self, session: Any | None = None):
        self.session = session

    def parse_recordset(self, payload: dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload, dict) and "schema" in payload and "records" in payload:
            return payload
        return {"schema": [], "records": []}

    def ensure_batch_constraints(self, configs: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        if not configs:
            return []

        batches: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_key: tuple[Any, ...] | None = None

        for cfg in configs:
            key = (
                cfg.get("region"),
                cfg.get("delay"),
                cfg.get("language"),
                cfg.get("instrumentType"),
            )
            if current and (key != current_key or len(current) >= 10):
                batches.append(current)
                current = []
            current_key = key
            current.append(cfg)

        if current:
            batches.append(current)

        return batches
