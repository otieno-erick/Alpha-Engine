from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ProviderConfig:
    name: str
    key_page: str
    requires_key: bool = True
    billed_to_user: bool = False
    free_tier: bool = False
    status: str = "ready"


@dataclass
class ModelConfig:
    name: str
    provider: str
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    max_prompt_tokens: int = 128000
    reset_timezone: str = "UTC"


@dataclass
class PromptVersion:
    name: str
    version: str
    text: str


class LLMHub:
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {
            "Google AI Studio": ProviderConfig("Google AI Studio", "https://aistudio.google.com/app/apikey", True, False, True),
            "Groq": ProviderConfig("Groq", "https://console.groq.com/keys", True, False, True),
            "Cerebras": ProviderConfig("Cerebras", "https://cloud.cerebras.ai/", True, False, True),
            "OpenRouter": ProviderConfig("OpenRouter", "https://openrouter.ai/keys", True, False, True),
            "NVIDIA NIM": ProviderConfig("NVIDIA NIM", "https://build.nvidia.com/explore/discover", True, False, True),
            "Mistral": ProviderConfig("Mistral", "https://console.mistral.ai/api-keys/", True, False, True),
            "GitHub Models": ProviderConfig("GitHub Models", "https://github.com/settings/tokens", True, False, True),
            "Hugging Face": ProviderConfig("Hugging Face", "https://huggingface.co/settings/tokens", True, False, True),
            "OpenAI": ProviderConfig("OpenAI", "https://platform.openai.com/api-keys", True, True, False),
            "Anthropic Claude": ProviderConfig("Anthropic Claude", "https://console.anthropic.com/settings/keys", True, True, False),
        }
        self.models: Dict[str, ModelConfig] = {
            "gemini-2.0-flash": ModelConfig("gemini-2.0-flash", "Google AI Studio", 60, 1000, 128000),
            "llama-3.3-70b": ModelConfig("llama-3.3-70b", "Groq", 60, 1000, 128000),
            "deepseek-r1": ModelConfig("deepseek-r1", "OpenRouter", 60, 1000, 128000),
            "gpt-4o-mini": ModelConfig("gpt-4o-mini", "OpenAI", 20, 500, 128000),
            "claude-3.5-sonnet": ModelConfig("claude-3.5-sonnet", "Anthropic Claude", 20, 500, 128000),
        }
        self.prompt_versions: Dict[str, PromptVersion] = {
            "alpha_generation": PromptVersion("alpha_generation", "v1", "Generate an alpha hypothesis with economic rationale and operator design."),
            "repair": PromptVersion("repair", "v1", "Repair the failing alpha with the exact failure, margin, and repair instruction."),
        }
        self.key_store: Dict[str, str] = {}

    def provider_cards(self) -> List[Dict[str, Any]]:
        cards = []
        for name, provider in self.providers.items():
            cards.append(
                {
                    "name": name,
                    "key_required": provider.requires_key,
                    "billed_to_user": provider.billed_to_user,
                    "free_tier": provider.free_tier,
                    "status": provider.status,
                    "key_page": provider.key_page,
                }
            )
        return cards

    def add_key(self, provider: str, key: str) -> None:
        self.key_store[provider] = key

    def model_setup(self, provider: str, model_name: str, *, rpm: int, rpd: int, reset_timezone: str, max_prompt_tokens: int) -> ModelConfig:
        cfg = ModelConfig(model_name, provider, rpm, rpd, max_prompt_tokens, reset_timezone)
        self.models[model_name] = cfg
        return cfg

    def route_request(self, provider_priority: Optional[List[str]] = None, *, required: bool = False) -> str:
        ordered = provider_priority or list(self.providers.keys())
        for provider_name in ordered:
            if provider_name in self.key_store or not required:
                return provider_name
        return ordered[0]

    def prompt_version(self, kind: str) -> PromptVersion:
        return self.prompt_versions[kind]

    def status(self) -> Dict[str, Any]:
        return {
            "providers": self.provider_cards(),
            "models": list(self.models.keys()),
            "prompt_versions": {k: v.version for k, v in self.prompt_versions.items()},
        }


DEFAULT_LLM_HUB = LLMHub()
