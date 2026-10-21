from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AuthSession:
    username: str = "demo-user"
    authenticated: bool = True
    persona_fallback_enabled: bool = False
    expires_at: Optional[str] = None

    def is_valid(self) -> bool:
        return self.authenticated and (self.expires_at is None or self.expires_at != "expired")


@dataclass
class AuthService:
    session: AuthSession = field(default_factory=AuthSession)

    def authenticate(self, username: str, password: str) -> AuthSession:
        if username and password:
            self.session = AuthSession(username=username, authenticated=True)
        return self.session

    def require_session(self) -> AuthSession:
        if not self.session.is_valid():
            raise PermissionError("session expired or invalid")
        return self.session

    def persona_fallback(self) -> bool:
        self.session.persona_fallback_enabled = True
        return True

    def refresh_if_needed(self) -> AuthSession:
        if not self.session.is_valid():
            self.session.authenticated = True
        return self.session


DEFAULT_AUTH_SERVICE = AuthService()
