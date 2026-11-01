from pathlib import Path

from app.services.runtime_security import RuntimeSecurity
from app.services.secret_store import SecretStore


def test_global_runtime_has_no_node_modules():
    repo_root = Path(__file__).resolve().parents[1]
    assert RuntimeSecurity.has_node_runtime(repo_root) is False


def test_global_runtime_stops_all_processes():
    active = {"backend": True, "worker": True, "child": False}
    result = RuntimeSecurity.stop_all(active)
    assert result == {"backend": False, "worker": False, "child": False}
    assert RuntimeSecurity.child_processes_stopped(result.values()) is True


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
