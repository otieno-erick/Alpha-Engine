import json
import sqlite3
import zipfile

from app.services.diagnostics import DiagnosticsBundle, redact


def test_diagnostics_bundle_removes_secrets(tmp_path):
    database_path = tmp_path / "source.db"
    connection = sqlite3.connect(database_path)
    connection.execute("CREATE TABLE settings (name TEXT, value TEXT)")
    connection.execute("INSERT INTO settings VALUES (?, ?)", ("api_key", "db-secret-value"))
    connection.commit()
    connection.close()

    secret_values = (
        "db-secret-value",
        "diagnostic-secret-value",
        "bearer-secret-value",
        "url-secret-value",
        "json-secret-value",
    )
    bundle_path = DiagnosticsBundle(
        app_version="0.1.0",
        database_path=database_path,
    ).create(
        tmp_path / "support.zip",
        diagnostics={
            "api_key": "diagnostic-secret-value",
            "headers": {"Authorization": "Bearer bearer-secret-value"},
            "error": (
                "api_key=diagnostic-secret-value "
                "Authorization: Bearer bearer-secret-value "
                "https://user:url-secret-value@example.test"
            ),
            "json_log": '{"password": "json-secret-value"}',
            "safe_value": "visible diagnostic detail",
        },
    )

    with zipfile.ZipFile(bundle_path) as bundle:
        assert bundle.namelist() == ["diagnostics.json"]
        contents = bundle.read("diagnostics.json").decode("utf-8")
        payload = json.loads(contents)

    assert all(secret not in contents for secret in secret_values)
    assert payload["diagnostics"]["safe_value"] == "visible diagnostic detail"
    assert payload["database"]["settings"][0]["value"] == "[REDACTED]"


def test_redact_handles_nested_values_and_sensitive_inline_fields():
    result = redact(
        {
            "nested": [{"refresh_token": "hidden", "label": "shown"}],
            "message": "password=hunter2 and Bearer abc123",
            "safe": 12,
        }
    )

    assert result["nested"] == [{"refresh_token": "[REDACTED]", "label": "shown"}]
    assert "hunter2" not in result["message"]
    assert "abc123" not in result["message"]
    assert result["safe"] == 12


def test_redact_scrubs_plaintext_credentials_from_messages():
    message = redact("password=hunter2 and Bearer abc123")

    assert "hunter2" not in message
    assert "abc123" not in message
