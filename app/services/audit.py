from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.db import get_connection, init_db


class AuditLog:
    def __init__(self):
        init_db()
        self._entries: list[dict[str, Any]] = []

    def log(self, action: str, detail: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "id": len(self._entries) + 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "detail": json.dumps(detail, sort_keys=True),
        }
        self._entries.append(entry)
        self._persist(entry)
        return entry

    def list_entries(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def _persist(self, entry: dict[str, Any]) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO audit_log (created_at, action, detail) VALUES (?, ?, ?)",
            (entry["created_at"], entry["action"], entry["detail"]),
        )
        conn.commit()
        conn.close()
