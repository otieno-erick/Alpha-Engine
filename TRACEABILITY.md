import pytest

from alpha_engine.phase4 import Alpha, AlphaPopup, Check, SubmissionPlanner


def make_alpha(*, alpha_id: str, failed: bool = False, description: str | None = None) -> Alpha:
    desc = description or ("This is a long enough description for submission. " * 3).strip()
    checks = {
        "turnover_floor": Check("turnover_floor", passed_=not failed),
        "correlation": Check("correlation", passed_=not failed),
    }
    return Alpha(
        id=alpha_id,
        expression="signal = alpha_1 + beta_2",
        dataset="USA_D0_TOP",
        description=desc,
        checks=checks,
    )


def test_submission_planner_excludes_failed_alpha():
    good = make_alpha(alpha_id="A-100", failed=False, description=("This is a valid alpha description that is long enough to pass the submission rules. " * 3).strip())
    bad = make_alpha(alpha_id="A-200", failed=True, description=("This is a valid alpha description that is long enough to pass the submission rules. " * 3).strip())

    planner = SubmissionPlanner([good, bad])
    ready = planner.ready_candidates()

    assert [a.id for a in ready] == ["A-100"]
    assert planner.zero_fail_candidates() == [good]


def test_submit_requires_confirmation_token():
    alpha = make_alpha(
        alpha_id="A-300",
        failed=False,
        description=("This description is long enough to satisfy the minimum description rule before confirmation is allowed. " * 3).strip(),
    )
    planner = SubmissionPlanner([alpha])

    with pytest.raises(ValueError):
        planner.submit(alpha.id, confirmation_token="")

    result = planner.submit(alpha.id, confirmation_token="confirm-123")
    assert result["submitted"] is True
    assert alpha.status == "submitted"


def test_alpha_popup_exposes_id_and_checks():
    alpha = make_alpha(
        alpha_id="A-400",
        failed=False,
        description=("This is a valid description for the popup test and it is long enough. " * 3).strip(),
    )
    popup = AlphaPopup(alpha)
    details = popup.details()

    assert details["id"] == "A-400"
    assert details["ready_to_submit"] is True
    assert "turnover_floor" in details["checks"]
    assert details["checks"]["correlation"]["passed"] is True
