from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Iterable


_NODE_PROCESS_NAMES = {"node", "nodejs"}


class RuntimeSecurity:
    """Checks the no-Node runtime policy and stops explicitly owned processes."""

    @staticmethod
    def has_node_runtime(root: str | Path | None = None) -> bool:
        base = Path(root) if root is not None else Path(__file__).resolve().parents[2]

        if (base / "node_modules").exists():
            return True
        if any(item.name == "node_modules" for item in base.rglob("node_modules")):
            return True

        try:
            import psutil
        except ImportError as exc:  # pragma: no cover - dependency is required by the app
            raise RuntimeError("psutil is required to verify the runtime process list") from exc

        current_process = psutil.Process()
        try:
            processes = [current_process, *current_process.children(recursive=True)]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            processes = [current_process]

        for proc in processes:
            try:
                name = proc.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if name.removesuffix(".exe") in _NODE_PROCESS_NAMES:
                return True
        return False

    @staticmethod
    def child_processes_stopped(active_processes: Iterable[Any]) -> bool:
        for process in active_processes or ():
            if process is None or process is False:
                continue
            if process is True:
                return False
            if isinstance(process, str):
                if process.strip().lower().removesuffix(".exe") in _NODE_PROCESS_NAMES:
                    return False
                continue
            poll = getattr(process, "poll", None)
            if poll is None or poll() is None:
                return False
        return True

    @staticmethod
    def stop_all(
        active_processes: dict[str, Any],
        *,
        timeout: float = 10,
    ) -> dict[str, bool]:
        stopped: dict[str, bool] = {}
        failures: dict[str, BaseException] = {}

        for name, process in (active_processes or {}).items():
            if process is None:
                stopped[name] = True
                continue

            poll = getattr(process, "poll", None)
            terminate = getattr(process, "terminate", None)
            wait = getattr(process, "wait", None)
            kill = getattr(process, "kill", None)
            if not all((poll, terminate, wait, kill)):
                raise TypeError(f"Managed process {name!r} must support poll, terminate, wait, and kill")

            if poll() is not None:
                stopped[name] = True
                continue

            try:
                terminate()
                try:
                    wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    kill()
                    wait(timeout=timeout)
            except (OSError, subprocess.TimeoutExpired) as exc:
                stopped[name] = poll() is not None
                if not stopped[name]:
                    failures[name] = exc
                continue

            stopped[name] = poll() is not None

        if failures or not all(stopped.values()):
            failed_names = sorted(name for name, is_stopped in stopped.items() if not is_stopped)
            failed_names.extend(name for name in failures if name not in failed_names)
            raise RuntimeError(f"Could not stop managed processes: {', '.join(failed_names)}") from next(
                iter(failures.values()), None
            )

        return stopped

    @staticmethod
    def secret_is_keychain_only(secret_store: Any, name: str, value: str) -> bool:
        if secret_store is None:
            return False
        secret_store.set_secret(name, value)
        return secret_store.get_secret(name) == value
