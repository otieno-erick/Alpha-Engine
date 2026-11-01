from __future__ import annotations

import json
from datetime import date
from typing import Any


DEFAULT_PROVIDER_SPECS: list[dict[str, Any]] = [
    {"name": "google_ai_studio", "label": "Google AI Studio", "key_url": "https://aistudio.google.com/app/apikey", "key_required": True},
    {"name": "groq", "label": "Groq", "key_url": "https://console.groq.com/keys", "key_required": True},
    {"name": "cerebras", "label": "Cerebras", "key_url": "https://cloud.cerebras.ai/", "key_required": True},
    {"name": "openrouter", "label": "OpenRouter", "key_url": "https://openrouter.ai/keys", "key_required": True},
    {"name": "nvidia_nim", "label": "NVIDIA NIM", "key_url": "https://build.nvidia.com/explore/discover", "key_required": True},
    {"name": "mistral", "label": "Mistral", "key_url": "https://console.mistral.ai/api-keys/", "key_required": True},
    {"name": "github_models", "label": "GitHub Models", "key_url": "https://github.com/settings/tokens", "key_required": True},
    {"name": "huggingface_free", "label": "Hugging Face (free)", "key_url": "https://huggingface.co/settings/tokens", "key_required": True},
    {"name": "openai", "label": "OpenAI", "key_url": "https://platform.openai.com/api-keys", "key_required": True},
    {"name": "anthropic_claude", "label": "Anthropic Claude", "key_url": "https://console.anthropic.com/settings/keys", "key_required": True},
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


class LLMBudgetLedger:
    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def record(self, *, provider: str, model: str, day: str | None = None, requests: int = 1) -> dict[str, Any]:
        day_key = day or date.today().isoformat()
        entry = {"provider": provider, "model": model, "day": day_key, "requests": requests}
        self.entries.append(entry)
        return entry

    def summary(self) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
        for entry in self.entries:
            key = (entry["provider"], entry["model"], entry["day"])
            bucket = grouped.setdefault(key, {"provider": entry["provider"], "model": entry["model"], "day": entry["day"], "requests": 0})
            bucket["requests"] += int(entry["requests"])
        return sorted(grouped.values(), key=lambda item: (item["day"], item["provider"], item["model"]))


class PromptVersioner:
    def __init__(self):
        self.versions: dict[str, str] = {}
        self.alpha_prompt_versions: dict[str, str] = {}

    def register(self, prompt_name: str, version: str) -> str:
        self.versions[prompt_name] = version
        return version

    def current_version(self, prompt_name: str, default: str = "v1") -> str:
        return self.versions.get(prompt_name, default)

    def record_alpha(self, alpha_id: str, prompt_name: str, version: str | None = None) -> str:
        prompt_version = version or self.current_version(prompt_name)
        self.alpha_prompt_versions[str(alpha_id)] = prompt_version
        return prompt_version

    def for_alpha(self, alpha_id: str) -> str | None:
        return self.alpha_prompt_versions.get(str(alpha_id))


class StructuredOutputParser:
    @staticmethod
    def parse(raw: str | None) -> dict[str, Any]:
        if raw is None:
            raise ValueError("LLM response was empty")
        text = raw.strip()
        if not text:
            raise ValueError("LLM response was empty")
        if text.startswith("```"):
            text = text.strip("`")
            text = text.strip()
            if text.lower().startswith("json"):
                text = text[4:].lstrip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:  # pragma: no cover - simple validation layer
            raise ValueError("Malformed structured output") from exc
        if not isinstance(payload, dict):
            raise ValueError("Structured LLM output must be a JSON object")
        return payload


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
        daily_cap: int | None = None,
        **meta: Any,
    ) -> None:
        cap = daily_cap if daily_cap is not None else max_per_day
        self.providers[name] = {
            "name": name,
            "max_per_minute": max_per_minute,
            "max_per_day": max_per_day,
            "daily_cap": cap,
            "available": True,
            **meta,
        }
        self.usage.setdefault(name, {"minute": 0, "day": 0})

    def _can_use(self, provider: dict[str, Any]) -> bool:
        usage = self.usage.get(provider["name"], {"minute": 0, "day": 0})
        day_cap = provider.get("daily_cap", provider.get("max_per_day", 1000))
        return (
            usage["minute"] < provider.get("max_per_minute", 60)
            and usage["day"] < day_cap
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
                "day": provider.get("daily_cap", provider.get("max_per_day", 1000)),
            },
        }


__all__ = [
    "DEFAULT_PROVIDER_SPECS",
    "LLMBudgetLedger",
    "LLMRouter",
    "PromptVersioner",
    "ProviderCatalog",
    "StructuredOutputParser",
    "default_provider_catalog",
]


if __name__ == "__main__":  # pragma: no cover
    catalog = default_provider_catalog()
    print(catalog.list_cards()[:3])
