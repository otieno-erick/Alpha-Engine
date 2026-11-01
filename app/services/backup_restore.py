from __future__ import annotations

import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


class BackupRestore:
    """Create and atomically restore SQLite database backups."""

    @staticmethod
    def _read_only_connection(path: Path) -> sqlite3.Connection:
        return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)

    @staticmethod
    def _validate_database(path: Path) -> None:
        try:
            with closing(BackupRestore._read_only_connection(path)) as connection:
                result = connection.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.DatabaseError as exc:
            raise ValueError(f"Invalid SQLite database: {path}") from exc
        if result is None or result[0] != "ok":
            raise ValueError(f"SQLite integrity check failed for: {path}")

    def backup(self, database_path: str | Path, destination: str | Path) -> Path:
        source = Path(database_path)
        backup_path = Path(destination)
        if not source.is_file():
            raise FileNotFoundError(f"Database does not exist: {source}")
        if source.resolve() == backup_path.resolve():
            raise ValueError("Backup destination must differ from the source database")

        self._validate_database(source)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._temporary_path(backup_path)
        try:
            self._copy_database(source, temporary_path)
            self._validate_database(temporary_path)
            os.replace(temporary_path, backup_path)
        finally:
            temporary_path.unlink(missing_ok=True)
        return backup_path

    def restore(self, backup_path: str | Path, database_path: str | Path) -> Path:
        source = Path(backup_path)
        destination = Path(database_path)
        if not source.is_file():
            raise FileNotFoundError(f"Backup does not exist: {source}")
        if source.resolve() == destination.resolve():
            raise ValueError("Restore source must differ from the database")

        self._validate_database(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._temporary_path(destination)
        try:
            self._copy_database(source, temporary_path)
            self._validate_database(temporary_path)
            os.replace(temporary_path, destination)
        finally:
            temporary_path.unlink(missing_ok=True)
        return destination

    @staticmethod
    def _temporary_path(destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            return Path(temporary.name)

    @staticmethod
    def _copy_database(source_path: Path, destination_path: Path) -> None:
        with closing(BackupRestore._read_only_connection(source_path)) as source:
            with closing(sqlite3.connect(destination_path)) as destination:
                source.backup(destination)
