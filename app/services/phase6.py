from __future__ import annotations

from collections import Counter
from typing import Any


class MobilePage:
    """Optional mobile dashboard that can require a token before access."""

    def __init__(self, *, enabled: bool = False, required_token: str | None = None):
        self.enabled = enabled
        self.required_token = required_token or ""

    def can_access(self, *, token: str | None = None) -> bool:
        if not self.enabled:
            return True
        return bool(self.required_token) and token == self.required_token


class AuditViewer:
    """Simple viewer for summarizing recent audit events."""

    def __init__(self, entries: list[dict[str, Any]] | None = None):
        self.entries = list(entries or [])

    def filter(
        self,
        *,
        event_type: str | None = None,
        actor: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for entry in self.entries:
            if event_type and entry.get("type") != event_type:
                continue
            if actor and entry.get("actor") != actor:
                continue
            if search:
                haystack = " ".join(
                    str(value)
                    for value in [
                        entry.get("type"),
                        entry.get("actor"),
                        entry.get("message"),
                        entry.get("detail"),
                    ]
                    if value is not None
                ).lower()
                if search.lower() not in haystack:
                    continue
            results.append(entry)
        return results

    def summarize(
        self,
        *,
        event_type: str | None = None,
        actor: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        filtered = self.filter(event_type=event_type, actor=actor, search=search)
        counts = Counter(str(item.get("type")) for item in filtered)
        return {
            "total": len(filtered),
            "by_type": dict(sorted(counts.items())),
            "latest": filtered[-1] if filtered else None,
        }


__all__ = ["MobilePage", "AuditViewer"]
