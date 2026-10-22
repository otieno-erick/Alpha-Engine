import keyring


class SecretStore:
    def __init__(self, service_name: str = "alpha-engine"):
        self.service_name = service_name

    def set_secret(self, name: str, value: str) -> None:
        keyring.set_password(self.service_name, name, value)

    def get_secret(self, name: str) -> str | None:
        return keyring.get_password(self.service_name, name)

    def delete_secret(self, name: str) -> None:
        keyring.delete_password(self.service_name, name)

