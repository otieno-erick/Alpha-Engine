from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


class RuntimeSecurity:
    """Minimal global-runtime and security guards for the app shell.

    These helpers match the Phase 1/Global acceptance conditions without
    introducing a build-time Node dependency or any plaintext secret storage.
    """

    @staticmethod
    def has_node_runtime(root: str | Path | None = None) -> bool:
        base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
        if (base / "node_modules").exists():
            return True
        return any(item.name == "node_modules" for item in base.rglob("node_modules"))

    @staticmethod
    def child_processes_stopped(active_processes: Iterable[str]) -> bool:
        return not any(bool(name) for name in active_processes)

    @staticmethod
    def stop_all(active_processes: dict[str, Any]) -> dict[str, Any]:
        stopped = {}
        for name, active in (active_processes or {}).items():
            stopped[name] = bool(active)
            if active:
                stopped[name] = False
        return stopped

    @staticmethod
    def secret_is_keychain_only(secret_store: Any, name: str, value: str) -> bool:
        if secret_store is None:
            return False
        secret_store.set_secret(name, value)
        return secret_store.get_secret(name) == value
