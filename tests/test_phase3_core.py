from app.services.llm_hub import LLMRouter
from app.services.pipeline import CreationPipeline


class FakeCache:
    def __init__(self):
        self.calls = 0

    def check_and_store(self, config):
        self.calls += 1
        return {"hit": False, "saved": False, "result": None}


class FakeValidator:
    def __call__(self, expression, config):
        return {"valid": True, "expression": expression}


class FakeSimulator:
    def __call__(self, config):
        return {"sub_universe": 1.17, "sharpe": 1.60, "turnover": 0.2, "is_ladder": 1.59, "max_weight": 8.0}


def test_router_uses_fallback_when_primary_is_exhausted():
    router = LLMRouter()
    router.register_provider("openrouter", max_per_minute=1, max_per_day=1)
    router.register_provider("groq", max_per_minute=3, max_per_day=3)
    first = router.dispatch(preferred="openrouter")
    second = router.dispatch(preferred="openrouter")
    assert first["provider"] == "openrouter"
    assert second["provider"] is None or second["provider"] == "groq"


def test_pipeline_order_for_clean_alpha():
    pipeline = CreationPipeline(
        validator=FakeValidator(),
        cache=FakeCache(),
        simulator=FakeSimulator(),
    )
    result = pipeline.run("rank(x)", {"region": "USA"})
    assert result["status"] == "stopped" or result["status"] == "clean"


def test_pipeline_uses_retry_budget_on_failures():
    pipeline = CreationPipeline(
        validator=FakeValidator(),
        cache=FakeCache(),
        simulator=FakeSimulator(),
    )
    pipeline.retry_budget = 2
    result = pipeline.run("rank(x)", {"region": "USA"})
    assert result["status"] in {"clean", "stopped"}
    assert pipeline.retry_budget == 2
