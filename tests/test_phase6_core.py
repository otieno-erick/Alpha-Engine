from app.services.phase6 import AuditViewer, MobilePageGuard


def test_mobile_page_requires_token_when_enabled():
    guard = MobilePageGuard(enabled=True, require_token=True)
    assert guard.allow_access(token=None) is False
    assert guard.allow_access(token="abc123") is True

    disabled = MobilePageGuard(enabled=False, require_token=True)
    assert disabled.allow_access(token="abc123") is False


def test_audit_viewer_filters_and_summarizes_events():
    viewer = AuditViewer(
        [
            {"user": "u1", "resource": "alpha", "status": "ok"},
            {"user": "u1", "resource": "alpha", "status": "failed"},
            {"user": "u2", "resource": "planner", "status": "ok"},
        ]
    )
    assert len(viewer.list_events(resource="alpha")) == 2
    assert len(viewer.list_events(user="u2")) == 1
    summary = viewer.failure_summary(resource="alpha")
    assert summary["total"] == 2
    assert summary["failures"] == 1
