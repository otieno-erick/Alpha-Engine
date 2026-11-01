import asyncio
import subprocess
from pathlib import Path

import psutil
import pytest

from app import main as app_main
from app.services.runtime_security import RuntimeSecurity
from app.services.secret_store import SecretStore


class FakeProcess:
    def __init__(self, *, timed_out_once=False):
        self.returncode = None
        self.terminated = False
        self.killed = False
        self.timed_out_once = timed_out_once

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        if not self.timed_out_once:
            self.returncode = 0

    def wait(self, timeout=None):
        if self.timed_out_once and not self.killed:
            raise subprocess.TimeoutExpired("fake-process", timeout)
        self.returncode = 0
        return self.returncode

    def kill(self):
        self.killed = True


def test_global_runtime_has_no_node_modules():
    repo_root = Path(__file__).resolve().parents[1]
    assert RuntimeSecurity.has_node_runtime(repo_root) is False


def test_global_runtime_ignores_unrelated_node_processes(monkeypatch, tmp_path):
    class Process:
        def name(self):
            return "python.exe"

        def children(self, recursive=False):
            return []

    monkeypatch.setattr(psutil, "Process", lambda: Process())
    assert RuntimeSecurity.has_node_runtime(tmp_path) is False


def test_global_runtime_detects_node_child_process(monkeypatch, tmp_path):
    class Process:
        def name(self):
            return "python.exe"

        def children(self, recursive=False):
            return [NodeProcess()]

    class NodeProcess:
        def name(self):
            return "node.exe"

    monkeypatch.setattr(psutil, "Process", lambda: Process())
    assert RuntimeSecurity.has_node_runtime(tmp_path) is True


def test_global_runtime_terminates_managed_processes():
    process = FakeProcess()
    already_stopped = FakeProcess()
    already_stopped.returncode = 0

    result = RuntimeSecurity.stop_all({"worker": process, "child": already_stopped})

    assert result == {"worker": True, "child": True}
    assert process.terminated is True
    assert RuntimeSecurity.child_processes_stopped([process, already_stopped]) is True


def test_global_runtime_kills_processes_that_do_not_terminate():
    process = FakeProcess(timed_out_once=True)

    result = RuntimeSecurity.stop_all({"worker": process}, timeout=0.01)

    assert result == {"worker": True}
    assert process.terminated is True
    assert process.killed is True


def test_global_runtime_rejects_unmanaged_process_values():
    with pytest.raises(TypeError, match="must support poll, terminate, wait, and kill"):
        RuntimeSecurity.stop_all({"worker": True})


def test_desktop_lifespan_stops_registered_children(monkeypatch):
    process = FakeProcess()
    monkeypatch.setitem(app_main.managed_child_processes, "worker", process)

    async def close_app():
        async with app_main.lifespan(app_main.app):
            pass

    asyncio.run(close_app())

    assert process.terminated is True
    assert app_main.managed_child_processes == {}


def test_secret_store_uses_keychain_not_plaintext(monkeypatch):
    calls = {}

    class FakeKeyring:
        @staticmethod
        def set_password(service, name, value):
            calls["set"] = (service, name, value)
            return None

        @staticmethod
        def get_password(service, name):
            if calls.get("set") == (service, name, "super-secret"):
                return "super-secret"
            return None

    monkeypatch.setattr("app.services.secret_store.keyring", FakeKeyring)
    secret_store = SecretStore(service_name="alpha-engine")

    assert secret_store.set_secret("brain-api-key", "super-secret") is None
    assert secret_store.get_secret("brain-api-key") == "super-secret"
    assert "super-secret" not in str(secret_store)
