import io
import json

import pytest
from fastapi import HTTPException

from app.main import check_for_updates
from app.services import auto_update
from app.services.auto_update import ReleaseUpdateChecker


class FakeResponse:
    def __init__(self, payload):
        self.payload = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self.payload

    def __exit__(self, *_args):
        self.payload.close()


def test_auto_update_checks_github_releases(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["accept"] = request.get_header("Accept")
        seen["user_agent"] = request.get_header("User-agent")
        seen["timeout"] = timeout
        return FakeResponse(
            {
                "tag_name": "v0.2.0",
                "html_url": "https://github.com/otieno-erick/Alpha-Engine/releases/tag/v0.2.0",
            }
        )

    monkeypatch.setattr(auto_update, "urlopen", fake_urlopen)
    checker = ReleaseUpdateChecker("0.1.0")

    result = checker.check()

    assert result == {
        "current_version": "0.1.0",
        "latest_version": "0.2.0",
        "update_available": True,
        "release_url": "https://github.com/otieno-erick/Alpha-Engine/releases/tag/v0.2.0",
    }
    assert seen == {
        "url": "https://api.github.com/repos/otieno-erick/Alpha-Engine/releases/latest",
        "accept": "application/vnd.github+json",
        "user_agent": "Alpha-Engine",
        "timeout": 10,
    }


def test_auto_update_does_not_report_current_release_as_an_update(monkeypatch):
    monkeypatch.setattr(
        auto_update,
        "urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {"tag_name": "v0.1.0", "html_url": "https://example.test/release"}
        ),
    )

    assert ReleaseUpdateChecker("0.1.0").check()["update_available"] is False


def test_auto_update_rejects_malformed_release(monkeypatch):
    monkeypatch.setattr(auto_update, "urlopen", lambda *_args, **_kwargs: FakeResponse({}))

    with pytest.raises(ValueError, match="missing tag_name or html_url"):
        ReleaseUpdateChecker("0.1.0").check()


def test_update_endpoint_reports_release_check_failures(monkeypatch):
    class FailedChecker:
        def check(self):
            raise OSError("GitHub unavailable")

    monkeypatch.setattr("app.main.update_checker", FailedChecker())

    with pytest.raises(HTTPException) as exc_info:
        check_for_updates()

    assert exc_info.value.status_code == 502
    assert "GitHub unavailable" in exc_info.value.detail
