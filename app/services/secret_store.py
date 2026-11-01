from __future__ import annotations


class SecretStore:
    def __init__(self, service_name: str = "alpha-engine"):
        self.service_name = service_name

    def set_secret(self, name: str, value: str) -> None:
        import keyring

        keyring.set_password(self.service_name, name, value)

    def get_secret(self, name: str) -> str | None:
        import keyring

        return keyring.get_password(self.service_name, name)

    def delete_secret(self, name: str) -> None:
        import keyring

        keyring.delete_password(self.service_name, name)

    def masked_value(self, name: str) -> str:
        return f"[redacted:{name}]"
