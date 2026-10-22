from app.services.diagnoser import Diagnoser
from app.services.rules import load_rules
from app.services.scorer import Scorer
from app.services.validator import validate_expression


def test_rules_lookup_reads_phase2_values():
    rules = load_rules()
    assert rules["rules.consultant_d1_sharpe"]["value"] == 1.58
    assert rules["rules.max_weight_fail_pct"]["value"] == 10.0
    assert rules["sub_universe_cutoff"]["value"] == 1.18


def test_validator_rejects_vector_field_without_vec_operator():
    try:
        validate_expression("strong_signal + 1.0", vector_fields=["strong_signal"], window=21)
        assert False, "Expected validation failure"
    except ValueError:
        pass


def test_validator_rejects_off_grid_window():
    try:
        validate_expression("rank(x) + 1", window=17)
        assert False, "Expected validation failure"
    except ValueError:
        pass


def test_scorer_reports_margin_for_sub_universe_example():
    rules = load_rules()
    scorer = Scorer(rules)
    result = scorer.evaluate({"sub_universe": 1.17})
    assert result["checks"][0]["margin"] == -0.01
    assert result["checks"][0]["passed"] is False


def test_scorer_applies_is_ladder_discount_for_low_turnover():
    rules = load_rules()
    scorer = Scorer(rules)
    result = scorer.evaluate({"turnover": 0.20, "is_ladder": 1.59})
    ladder_check = next(check for check in result["checks"] if check["id"] == "is_ladder")
    assert ladder_check["value"] == 1.3515
    assert ladder_check["passed"] is False


def test_diagnoser_returns_first_failure_and_repair_instruction():
    checks = [
        {"id": "max_weight", "passed": True},
        {"id": "turnover", "passed": True},
        {"id": "is_ladder", "passed": False},
        {"id": "sharpe", "passed": False},
    ]
    diagnosis = Diagnoser().diagnose(checks)
    assert diagnosis["first_failure"] == "is_ladder"
    assert diagnosis["repair_instruction"] == "IS Ladder"
    assert diagnosis["repair_type"] == "repair"
