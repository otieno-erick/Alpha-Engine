from __future__ import annotations

from typing import Any


class LLMRouter:
    """Simple provider router for the Alpha Engine LLM layer.

    It enforces per-provider rate limits and fails over to the next available
    provider when the preferred option is exhausted.
    """

    def __init__(self, providers: dict[str, dict[str, Any]] | None = None):
        self.providers: dict[str, dict[str, Any]] = providers or {}
        self.usage: dict[str, dict[str, int]] = {}

    def register_provider(
        self,
        name: str,
        *,
        max_per_minute: int = 60,
        max_per_day: int = 1000,
        **meta: Any,
    ) -> None:
        self.providers[name] = {
            "name": name,
            "max_per_minute": max_per_minute,
            "max_per_day": max_per_day,
            "available": True,
            **meta,
        }
        self.usage.setdefault(name, {"minute": 0, "day": 0})

    def _can_use(self, provider: dict[str, Any]) -> bool:
        usage = self.usage.get(provider["name"], {"minute": 0, "day": 0})
        return (
            usage["minute"] < provider.get("max_per_minute", 60)
            and usage["day"] < provider.get("max_per_day", 1000)
        )

    def choose_provider(self, *, preferred: str | None = None) -> str | None:
        if preferred and preferred in self.providers:
            provider = self.providers[preferred]
            if self._can_use(provider):
                return preferred

        for name in self.providers:
            provider = self.providers[name]
            if self._can_use(provider):
                return name
        return None

    def dispatch(self, *, preferred: str | None = None) -> dict[str, Any]:
        provider_name = self.choose_provider(preferred=preferred)
        if provider_name is None:
            return {"provider": None, "status": "exhausted", "fallback": False}

        provider = self.providers[provider_name]
        self.usage.setdefault(provider_name, {"minute": 0, "day": 0})
        self.usage[provider_name]["minute"] += 1
        self.usage[provider_name]["day"] += 1

        return {
            "provider": provider_name,
            "status": "ok",
            "fallback": preferred is not None and provider_name != preferred,
            "limit": {
                "minute": provider.get("max_per_minute", 60),
                "day": provider.get("max_per_day", 1000),
            },
        }
