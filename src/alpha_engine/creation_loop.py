from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Session:
    authenticated: bool = False
    username: str = "guest"


class AuthService:
    def __init__(self):
        self.session = Session()

    def login(self, username: str, password: str) -> bool:
        self.session = Session(authenticated=True, username=username)
        return True

    def logout(self) -> None:
        self.session = Session()

    def summary(self) -> Dict[str, Any]:
        return {"authenticated": self.session.authenticated, "username": self.session.username}


DEFAULT_AUTH_SERVICE = AuthService()
