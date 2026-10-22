from app.services.submission import AlphaDetail, SubmissionPlanner


def test_submission_requires_explicit_confirmation():
    planner = SubmissionPlanner()
    alpha = {"id": "A-100", "checks": [{"passed": True}]}
    assert planner.can_submit(alpha, confirm_token=None) is False
    assert planner.can_submit(alpha, confirm_token="confirmed") is True


def test_submission_rejects_failed_alpha():
    planner = SubmissionPlanner()
    alpha = {"id": "A-101", "checks": [{"passed": False}]}
    assert planner.submit(alpha, confirm_token="confirmed")["submitted"] is False


def test_alpha_detail_exposes_core_fields():
    alpha = {
        "id": "A-102",
        "expression": "rank(x)",
        "dataset": "USA_EQ",
        "hypothesis": "Momentum continuation",
        "settings": {"region": "USA"},
        "lineage": {"parent": "seed-1"},
        "checks": [{"id": "sub_universe", "passed": True}],
    }
    detail = AlphaDetail.from_alpha(alpha)
    assert detail.payload()["id"] == "A-102"
    assert detail.payload()["dataset"] == "USA_EQ"
    assert detail.payload()["checks"][0]["id"] == "sub_universe"
