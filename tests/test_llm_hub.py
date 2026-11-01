from __future__ import annotations

from app.services.llm_hub import default_provider_catalog


def test_provider_catalog_includes_all_required_cards():
    cards = default_provider_catalog().list_cards()
    names = {card["name"] for card in cards}
    required = {
        "google_ai_studio",
        "groq",
        "cerebras",
        "openrouter",
        "nvidia_nim",
        "mistral",
        "github_models",
        "huggingface_free",
        "openai",
        "anthropic_claude",
    }
    assert required.issubset(names)


def test_provider_cards_include_key_url_and_key_required_flag():
    catalog = default_provider_catalog()
    openai = catalog.by_name("openai")
    assert openai is not None
    assert openai["key_url"].startswith("https://")
    assert openai["key_required"] is True


def test_router_uses_fallback_when_primary_is_exhausted():
    router = __import__("app.services.llm_hub", fromlist=["LLMRouter"]).LLMRouter()
    router.register_provider("openai", max_per_minute=1, max_per_day=2)
    router.register_provider("groq", max_per_minute=5, max_per_day=20)

    first = router.dispatch(preferred="openai")
    second = router.dispatch(preferred="openai")

    assert first["provider"] == "openai"
    assert second["provider"] == "groq"
    assert second["fallback"] is True
