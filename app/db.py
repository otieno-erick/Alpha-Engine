from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "alpha_engine.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            slots INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alpha_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alpha_id TEXT NOT NULL,
            dataset TEXT NOT NULL,
            status TEXT NOT NULL,
            expression TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def get_cached_alphas() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT alpha_id, dataset, status, expression, created_at FROM alpha_cache ORDER BY id DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
