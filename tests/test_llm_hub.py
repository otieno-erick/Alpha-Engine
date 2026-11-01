from app.services.llm_hub import (
    LLMBudgetLedger,
    LLMRouter,
    PromptVersioner,
    ProviderCatalog,
    StructuredOutputParser,
    default_provider_catalog,
)


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
    router = LLMRouter()
    router.register_provider("openai", max_per_minute=1, max_per_day=2)
    router.register_provider("groq", max_per_minute=5, max_per_day=20)

    first = router.dispatch(preferred="openai")
    second = router.dispatch(preferred="openai")

    assert first["provider"] == "openai"
    assert second["provider"] == "groq"
    assert second["fallback"] is True


def test_budget_ledger_summarizes_requests_by_provider_model_and_day():
    ledger = LLMBudgetLedger()
    ledger.record(provider="openai", model="gpt-4o-mini", day="2026-11-01", requests=2)
    ledger.record(provider="openai", model="gpt-4o-mini", day="2026-11-01", requests=3)
    ledger.record(provider="groq", model="llama-3.1-70b", day="2026-11-01", requests=5)

    summary = ledger.summary()
    by_provider = {row["provider"]: row["requests"] for row in summary}
    assert by_provider["openai"] == 5
    assert by_provider["groq"] == 5


def test_prompt_versioner_tracks_alpha_prompt_versions():
    versioner = PromptVersioner()
    versioner.register("base-alpha", "v3")
    versioner.record_alpha("A-120", "base-alpha")

    assert versioner.current_version("base-alpha") == "v3"
    assert versioner.for_alpha("A-120") == "v3"


def test_structured_output_parser_rejects_malformed_json():
    try:
        StructuredOutputParser.parse("{not valid json}")
        assert False, "Expected malformed JSON to raise ValueError"
    except ValueError:
        pass


def test_provider_catalog_registers_named_provider():
    catalog = ProviderCatalog()
    catalog.register("custom-provider", label="Custom Provider", key_url="https://example.com", key_required=True)
    assert catalog.by_name("custom-provider")["label"] == "Custom Provider"
