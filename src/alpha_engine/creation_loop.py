from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import os


@dataclass
class EventRecord:
    timestamp: str
    level: str
    message: str
    meta: Dict[str, Any] = field(default_factory=dict)


class AuditLog:
    def __init__(self):
        self.events: List[EventRecord] = []

    def record(self, level: str, message: str, **meta: Any) -> EventRecord:
        event = EventRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            message=message,
            meta=meta,
        )
        self.events.append(event)
        return event

    def summary(self) -> Dict[str, Any]:
        return {
            "count": len(self.events),
            "levels": {level: sum(1 for e in self.events if e.level == level) for level in sorted({e.level for e in self.events})},
            "last_message": self.events[-1].message if self.events else None,
        }


class SecretVault:
    def __init__(self, env_prefix: str = "ALPHA_ENGINE_"):
        self.env_prefix = env_prefix

    def _env_name(self, provider: str) -> str:
        return f"{self.env_prefix}{provider.upper().replace(' ', '_').replace('-', '_')}"

    def store(self, provider: str, value: str) -> str:
        env_name = self._env_name(provider)
        os.environ[env_name] = value
        return env_name

    def get(self, provider: str) -> Optional[str]:
        return os.environ.get(self._env_name(provider))

    def masked(self, provider: str) -> Optional[str]:
        value = self.get(provider)
        if not value:
            return None
        if len(value) <= 6:
            return "***"
        return f"{value[:4]}...{value[-2:]}"


class StopAllController:
    def __init__(self):
        self.triggered = False

    def stop_all(self) -> bool:
        self.triggered = True
        return self.triggered

    def resume(self) -> bool:
        self.triggered = False
        return self.triggered

    def status(self) -> Dict[str, bool]:
        return {"stopped": self.triggered}


DEFAULT_AUDIT_LOG = AuditLog()
DEFAULT_SECRET_VAULT = SecretVault()
DEFAULT_STOP_ALL = StopAllController()

