from __future__ import annotations

from typing import Any


DEFAULT_PROVIDER_SPECS: list[dict[str, Any]] = [
    {
        "name": "google_ai_studio",
        "label": "Google AI Studio",
        "key_url": "https://aistudio.google.com/app/apikey",
        "key_required": True,
    },
    {
        "name": "groq",
        "label": "Groq",
        "key_url": "https://console.groq.com/keys",
        "key_required": True,
    },
    {
        "name": "cerebras",
        "label": "Cerebras",
        "key_url": "https://cloud.cerebras.ai/",
        "key_required": True,
    },
    {
        "name": "openrouter",
        "label": "OpenRouter",
        "key_url": "https://openrouter.ai/keys",
        "key_required": True,
    },
    {
        "name": "nvidia_nim",
        "label": "NVIDIA NIM",
        "key_url": "https://build.nvidia.com/explore/discover",
        "key_required": True,
    },
    {
        "name": "mistral",
        "label": "Mistral",
        "key_url": "https://console.mistral.ai/api-keys/",
        "key_required": True,
    },
    {
        "name": "github_models",
        "label": "GitHub Models",
        "key_url": "https://github.com/settings/tokens",
        "key_required": True,
    },
    {
        "name": "huggingface_free",
        "label": "Hugging Face (free)",
        "key_url": "https://huggingface.co/settings/tokens",
        "key_required": True,
    },
    {
        "name": "openai",
        "label": "OpenAI",
        "key_url": "https://platform.openai.com/api-keys",
        "key_required": True,
    },
    {
        "name": "anthropic_claude",
        "label": "Anthropic Claude",
        "key_url": "https://console.anthropic.com/settings/keys",
        "key_required": True,
    },
]


class ProviderCatalog:
    """Catalog for the LLM providers shown in the Providers tab."""

    def __init__(self, providers: dict[str, dict[str, Any]] | None = None):
        self.providers: dict[str, dict[str, Any]] = {}
        if providers:
            for name, config in providers.items():
                self.register(name, **config)
        else:
            for spec in DEFAULT_PROVIDER_SPECS:
                self.register(
                    spec["name"],
                    label=spec.get("label", spec["name"]),
                    key_url=spec.get("key_url"),
                    key_required=spec.get("key_required", True),
                )

    def register(
        self,
        name: str,
        *,
        label: str | None = None,
        key_url: str | None = None,
        key_required: bool = True,
        **meta: Any,
    ) -> None:
        self.providers[name] = {
            "name": name,
            "label": label or name,
            "key_url": key_url,
            "key_required": key_required,
            **meta,
        }

    def list_cards(self) -> list[dict[str, Any]]:
        return [dict(provider) for provider in self.providers.values()]

    def by_name(self, name: str) -> dict[str, Any] | None:
        return self.providers.get(name)


def default_provider_catalog() -> ProviderCatalog:
    return ProviderCatalog()


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
