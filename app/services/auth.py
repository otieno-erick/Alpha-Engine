from __future__ import annotations

from typing import Any


def should_trigger_persona(response: Any) -> bool:
    if response is None:
        return False
    headers = getattr(response, "headers", {}) or {}
    return getattr(response, "status_code", 0) == 401 and headers.get("WWW-Authenticate") == "persona"


def is_session_expired(response: Any) -> bool:
    if response is None:
        return False

    status_code = getattr(response, "status_code", 0)
    if status_code != 401:
        return False

    headers = getattr(response, "headers", {}) or {}
    if headers.get("WWW-Authenticate") == "persona":
        return False

    payload = {}
    if hasattr(response, "json"):
        try:
            payload = response.json() if callable(response.json) else response.json
        except Exception:
            payload = {}

    if isinstance(payload, dict):
        error_value = payload.get("error") or payload.get("error_code")
        if error_value in {"expired_session", "session_expired", "token_expired"}:
            return True

    auth_status = headers.get("X-Auth-Status") or headers.get("X-Auth-Reason")
    if auth_status in {"expired", "session_expired", "token_expired"}:
        return True

    return True


def needs_reauth(response: Any) -> bool:
    return should_trigger_persona(response) or is_session_expired(response)
