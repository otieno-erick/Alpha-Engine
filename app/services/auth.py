from __future__ import annotations

from typing import Any


def should_trigger_persona(response: Any) -> bool:
    if response is None:
        return False
    headers = getattr(response, "headers", {}) or {}
    return getattr(response, "status_code", 0) == 401 and headers.get("WWW-Authenticate") == "persona"


def needs_reauth(response: Any) -> bool:
    return getattr(response, "status_code", 0) == 401
