from alpha_engine.creation_loop import CreationLoop
from alpha_engine.llm_hub import LLMHub


def test_llm_hub_has_provider_cards_and_model_setup():
    hub = LLMHub()
    cards = hub.provider_cards()
    assert len(cards) >= 10
    assert any(card["name"] == "OpenAI" for card in cards)
    cfg = hub.model_setup("OpenAI", "gpt-4o-mini", rpm=30, rpd=250, reset_timezone="UTC", max_prompt_tokens=128000)
    assert cfg.provider == "OpenAI"
    assert cfg.requests_per_minute == 30


def test_creation_loop_generates_hypotheses_and_lineage():
    loop = CreationLoop()
    result = loop.run_pipeline({"datasets": ["USA_D0_TOP"], "prompt_version": "alpha_generation"})
    assert result["count"] == 1
    assert loop.hypotheses[0].dataset == "USA_D0_TOP"
    assert len(loop.lineage) == 1


def test_prompt_versions_are_recorded():
    hub = LLMHub()
    prompt = hub.prompt_version("alpha_generation")
    assert prompt.version == "v1"
    assert "alpha" in prompt.text.lower()
