from __future__ import annotations

import json
import re
import sqlite3
import zipfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_SENSITIVE_KEY = re.compile(
    r"(?:authorization|api[_-]?(?:key|token)|access[_-]?token|refresh[_-]?token|"
    r"password|passwd|secret|credential|cookie|session[_-]?id)",
    re.IGNORECASE,
)
_BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
_KEY_VALUE_SECRET = re.compile(
    r"""(?i)(["']?(?:api[_-]?(?:key|token)|access[_-]?token|refresh[_-]?token|"""
    r"""password|passwd|secret|authorization)["']?\s*[:=]\s*)"""
    r"""(?:"[^"]*"|'[^']*'|[^\s,;}\]]+)"""
)
_URL_CREDENTIALS = re.compile(r"(://[^:/@\s]+:)[^@\s]+@")
_REDACTED = "[REDACTED]"


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _REDACTED if _SENSITIVE_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        value = _BEARER_TOKEN.sub("Bearer [REDACTED]", value)
        value = _KEY_VALUE_SECRET.sub(r"\1[REDACTED]", value)
        return _URL_CREDENTIALS.sub(r"\1[REDACTED]@", value)
    if isinstance(value, bytes):
        return "[BINARY DATA]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


class DiagnosticsBundle:
    def __init__(self, *, app_version: str, database_path: str | Path):
        self.app_version = app_version
        self.database_path = Path(database_path)

    def _database_snapshot(self) -> dict[str, list[dict[str, Any]]]:
        if not self.database_path.exists():
            return {}

        database_uri = f"{self.database_path.resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(database_uri, uri=True)
        try:
            table_names = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            snapshot: dict[str, list[dict[str, Any]]] = {}
            for table in table_names:
                escaped_table = table.replace('"', '""')
                cursor = connection.execute(f'SELECT * FROM "{escaped_table}"')
                columns = [column[0] for column in cursor.description or ()]
                rows = []
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    setting_name = next(
                        (
                            record[key]
                            for key in ("name", "key", "setting")
                            if isinstance(record.get(key), str)
                        ),
                        None,
                    )
                    if setting_name and _SENSITIVE_KEY.search(setting_name):
                        for value_key in ("value", "content", "data"):
                            if value_key in record:
                                record[value_key] = _REDACTED
                    rows.append(redact(record))
                snapshot[table] = rows
            return snapshot
        finally:
            connection.close()

    def create(self, destination: str | Path, *, diagnostics: Mapping[str, Any] | None = None) -> Path:
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "app_version": self.app_version,
            "diagnostics": redact(diagnostics or {}),
            "database": self._database_snapshot(),
        }
        with zipfile.ZipFile(destination_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr(
                "diagnostics.json",
                json.dumps(payload, indent=2, sort_keys=True),
            )
        return destination_path
