from app.services.phase6 import AuditViewer, MobilePage


def test_mobile_page_requires_token_when_enabled():
    page = MobilePage(enabled=True, required_token="secret-token")
    assert page.can_access() is False
    assert page.can_access(token="secret-token") is True
    assert MobilePage(enabled=False).can_access() is True


def test_audit_viewer_filters_and_summarizes_events():
    entries = [
        {"type": "simulation_sent", "actor": "user", "message": "alpha sent"},
        {"type": "simulation_sent", "actor": "llm", "message": "prompt retry"},
        {"type": "quota_blocked", "actor": "system", "message": "quota exhaust"},
    ]
    viewer = AuditViewer(entries)

    filtered = viewer.filter(event_type="simulation_sent")
    assert len(filtered) == 2
    assert viewer.filter(search="quota")[0]["type"] == "quota_blocked"

    summary = viewer.summarize()
    assert summary["total"] == 3
    assert summary["by_type"]["simulation_sent"] == 2
    assert summary["latest"]["type"] == "quota_blocked"
