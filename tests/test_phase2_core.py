from alpha_engine.rules_registry import RulesRegistry
from alpha_engine.validator import Validator
from alpha_engine.scorer import Scorer
from alpha_engine.diagnoser import Diagnoser


def test_rules_registry_lookup_rules():
    registry = RulesRegistry()
    assert registry.lookup(key="turnover_floor", tier="user", delay="D0", region="USA", universe="TOP") == 0.125
    assert registry.lookup(key="power_pool_limit", tier="user", delay="D0", region="ALL", universe="TOP") == 8


def test_validator_rejects_bad_expression():
    validator = Validator(allowed_fields=("alpha_1", "beta_2"))
    result = validator.validate_expression("alpha_1 + ; beta_2")
    assert result.valid is False
    assert any("unsupported" in error for error in result.errors)


def test_scorer_flags_clear_alpha():
    scorer = Scorer()
    result = scorer.score_alpha({"turnover": 0.30, "sharpe": 1.80, "correlation": 0.50, "fitness": 0.10})
    assert any(check.name == "turnover_floor" and check.passed for check in result)
    assert scorer.clean_alpha({"turnover": 0.30, "sharpe": 1.80, "correlation": 0.50, "fitness": 0.10}) is True


def test_diagnoser_maps_first_failure():
    diagnoser = Diagnoser()
    checks = [
        {"name": "turnover_floor", "passed": True, "margin": 0.2},
        {"name": "correlation", "passed": False, "margin": -0.15},
    ]
    result = diagnoser.diagnose(checks)
    assert result["first_failure"] == "correlation"
    assert "dataset" in result["action"].lower() or "region" in result["action"].lower()

