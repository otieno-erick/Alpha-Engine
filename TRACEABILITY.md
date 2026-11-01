from app.db import get_cached_alphas, get_connection, init_db


def test_app_loads_cached_alphas_offline(tmp_path, monkeypatch):
    db_path = tmp_path / "alpha_engine.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)
    init_db()

    conn = get_connection()
    conn.execute(
        "INSERT INTO alpha_cache (alpha_id, dataset, status, expression, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("A-100", "USA_EQ", "pending", "rank(x)",),
    )
    conn.commit()
    conn.close()

    rows = get_cached_alphas()
    assert len(rows) == 1
    assert rows[0]["alpha_id"] == "A-100"
    assert rows[0]["dataset"] == "USA_EQ"
    assert rows[0]["status"] == "pending"
