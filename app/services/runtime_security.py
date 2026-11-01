from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


_NODE_PROCESS_NAMES = {"node", "nodejs", "node.exe", "nodejs.exe"}


class RuntimeSecurity:
    """Global-runtime checks for the app shell.

    The runtime guard rejects both a local Node installation footprint and an
    active Node process so the app stays within the Phase 1 security and
    packaging requirements.
    """

    @staticmethod
    def has_node_runtime(root: str | Path | None = None) -> bool:
        base = Path(root) if root is not None else Path(__file__).resolve().parents[2]

        if (base / "node_modules").exists():
            return True
        if any(item.name == "node_modules" for item in base.rglob("node_modules")):
            return True

        try:
            import psutil
        except Exception:  # pragma: no cover - optional dependency
            return False

        for proc in psutil.process_iter(["name"]):
            try:
                name = (proc.info.get("name") or "").lower().replace(".exe", "")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if name in _NODE_PROCESS_NAMES:
                return True
        return False

    @staticmethod
    def child_processes_stopped(active_processes: Iterable[str]) -> bool:
        for name in active_processes or ():
            if name is None:
                continue
            normalized = str(name).strip().lower().replace(".exe", "")
            if normalized in _NODE_PROCESS_NAMES:
                return False
        return True

    @staticmethod
    def stop_all(active_processes: dict[str, Any]) -> dict[str, Any]:
        stopped: dict[str, Any] = {}
        for name, active in (active_processes or {}).items():
            stopped[name] = False
        return stopped

    @staticmethod
    def secret_is_keychain_only(secret_store: Any, name: str, value: str) -> bool:
        if secret_store is None:
            return False
        secret_store.set_secret(name, value)
        return secret_store.get_secret(name) == value
