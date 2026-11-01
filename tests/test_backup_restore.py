import sqlite3

import pytest

from app.services.backup_restore import BackupRestore


def create_database(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    connection.execute("INSERT INTO state VALUES ('status', ?)", (value,))
    connection.commit()
    connection.close()


def read_database_value(path):
    connection = sqlite3.connect(path)
    try:
        return connection.execute("SELECT value FROM state WHERE key='status'").fetchone()[0]
    finally:
        connection.close()


def test_backup_restore_reproduces_local_data_state(tmp_path):
    database = tmp_path / "app-data" / "alpha_engine.db"
    backup = tmp_path / "backups" / "alpha_engine.db"
    restored_database = tmp_path / "restored" / "alpha_engine.db"
    create_database(database, "before")

    service = BackupRestore()
    assert service.backup(database, backup) == backup
    assert read_database_value(backup) == "before"

    create_database(restored_database, "after")
    assert service.restore(backup, restored_database) == restored_database
    assert read_database_value(restored_database) == "before"


def test_restore_rejects_invalid_backup_without_changing_database(tmp_path):
    backup = tmp_path / "invalid.db"
    backup.write_text("not a database", encoding="utf-8")
    database = tmp_path / "app.db"
    create_database(database, "keep")

    with pytest.raises(ValueError, match="Invalid SQLite database"):
        BackupRestore().restore(backup, database)

    assert read_database_value(database) == "keep"


def test_backup_rejects_same_source_and_destination(tmp_path):
    database = tmp_path / "app.db"
    create_database(database, "state")

    with pytest.raises(ValueError, match="must differ"):
        BackupRestore().backup(database, database)


def test_restore_rejects_same_source_and_destination(tmp_path):
    database = tmp_path / "app.db"
    create_database(database, "state")

    with pytest.raises(ValueError, match="must differ"):
        BackupRestore().restore(database, database)
