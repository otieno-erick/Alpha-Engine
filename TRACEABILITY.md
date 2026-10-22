from alpha_engine.phase5 import AuditLog, SecretVault, StopAllController


def test_audit_log_records_events_and_summary():
    log = AuditLog()
    evt = log.record("INFO", "submission started", alpha_id="A-1")
    assert evt.level == "INFO"
    assert log.summary()["count"] == 1
    assert log.summary()["last_message"] == "submission started"


def test_secret_vault_masks_and_stores_values():
    vault = SecretVault(env_prefix="TEST_ENGINE_")
    env_name = vault.store("OpenAI", "sk-abc123456789")
    assert env_name.endswith("OPENAI")
    assert vault.get("OpenAI") == "sk-abc123456789"
    assert vault.masked("OpenAI").startswith("sk-")


def test_stop_all_controller_blocks_runtime():
    controller = StopAllController()
    assert controller.status()["stopped"] is False
    assert controller.stop_all() is True
    assert controller.status()["stopped"] is True
    assert controller.resume() is False
