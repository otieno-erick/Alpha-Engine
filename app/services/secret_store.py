from __future__ import annotations

try:
    import keyring
except Exception:  # pragma: no cover - fallback for environments without keyring
    class _MissingKeyring:
        @staticmethod
        def set_password(*args, **kwargs):
            return None

        @staticmethod
        def get_password(*args, **kwargs):
            return None

        @staticmethod
        def delete_password(*args, **kwargs):
            return None

    keyring = _MissingKeyring()


class SecretStore:
    def __init__(self, service_name: str = "alpha-engine"):
        self.service_name = service_name

    def set_secret(self, name: str, value: str) -> None:
        keyring.set_password(self.service_name, name, value)

    def get_secret(self, name: str) -> str | None:
        return keyring.get_password(self.service_name, name)

    def delete_secret(self, name: str) -> None:
        keyring.delete_password(self.service_name, name)

    def masked_value(self, name: str) -> str:
        return f"[redacted:{name}]"
