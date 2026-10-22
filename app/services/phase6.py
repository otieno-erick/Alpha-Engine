from __future__ import annotations

from typing import Any


class MobilePageGuard:
    """Simple mobile access gate for the optional monitoring page."""

    def __init__(self, *, enabled: bool = False, require_token: bool = True):
        self.enabled = enabled
        self.require_token = require_token

    def allow_access(self, *, token: str | None = None) -> bool:
        if not self.enabled:
            return False
        if not self.require_token:
            return True
        return bool(token)


class AuditViewer:
    """Minimal viewer for audit events and failure analytics."""

    def __init__(self, events: list[dict[str, Any]] | None = None):
        self.events = events or []

    def list_events(self, *, resource: str | None = None, user: str | None = None) -> list[dict[str, Any]]:
        filtered = list(self.events)
        if resource is not None:
            filtered = [event for event in filtered if event.get("resource") == resource]
        if user is not None:
            filtered = [event for event in filtered if event.get("user") == user]
        return filtered

    def failure_summary(self, *, resource: str | None = None) -> dict[str, Any]:
        matching = self.list_events(resource=resource)
        failures = [event for event in matching if event.get("status") == "failed"]
        return {"total": len(matching), "failures": len(failures), "resource": resource}
