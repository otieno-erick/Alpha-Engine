import asyncio
import subprocess
from pathlib import Path

import psutil
import pytest

from app import main as app_main
from app import db
from app.desktop import _smoke_test
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


def test_desktop_smoke_test_starts_and_stops_backend():
    _smoke_test()


@pytest.mark.parametrize(
    ("system", "environment", "expected"),
    [
        ("Windows", {"LOCALAPPDATA": "C:/Users/test/AppData/Local"}, "C:/Users/test/AppData/Local/AlphaEngine"),
        ("Darwin", {}, "HOME/Library/Application Support/AlphaEngine"),
        ("Linux", {"XDG_DATA_HOME": "/home/test/.local/share"}, "/home/test/.local/share/alpha-engine"),
    ],
)
def test_database_uses_platform_user_data_directory(
    monkeypatch, tmp_path, system, environment, expected
):
    monkeypatch.setattr(db.platform, "system", lambda: system)
    monkeypatch.setattr(db.Path, "home", lambda: tmp_path)
    monkeypatch.delenv("ALPHA_ENGINE_DATA_DIR", raising=False)
    for key in ("LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.delenv(key, raising=False)
    for key, value in environment.items():
        monkeypatch.setenv(key, value)

    path = db.user_data_directory()
    expected_path = Path(expected.replace("HOME", str(tmp_path)))

    assert path == expected_path


def test_database_supports_an_explicit_data_directory(monkeypatch, tmp_path):
    configured = tmp_path / "custom-data"
    monkeypatch.setenv("ALPHA_ENGINE_DATA_DIR", str(configured))

    assert db.user_data_directory() == configured


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
