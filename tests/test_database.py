import sqlite3
import pytest
from db.database import get_connection, init_db
from db.import_json import import_all, normalize_date


def test_normalize_date():
    assert normalize_date("20.10.2026") == "2026-10-20"
    assert normalize_date("2026-10-20") == "2026-10-20"
    assert normalize_date("01.01.2025") == "2025-01-01"


def test_database_initialization_and_schema(tmp_path):
    test_db = tmp_path / "test_calendar.sqlite"
    init_db(test_db)
    conn = get_connection(test_db)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    tables = [row["name"] for row in cursor.fetchall()]
    assert "categories" in tables
    assert "users" in tables
    assert "events" in tables

    # Проверка внешних ключей в таблице events
    fk_list = conn.execute("PRAGMA foreign_key_list(events);").fetchall()
    fk_tables = {row["table"] for row in fk_list}
    assert "users" in fk_tables
    assert "categories" in fk_tables
    conn.close()


def test_database_import_and_integrity(tmp_path):
    test_db = tmp_path / "test_calendar.sqlite"
    import_all(test_db)
    conn = get_connection(test_db)

    cat_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM categories;"
    ).fetchone()["cnt"]
    user_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM users;"
    ).fetchone()["cnt"]
    event_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM events;"
    ).fetchone()["cnt"]

    assert cat_count == 5
    assert user_count == 3
    assert event_count >= 5

    # Проверка целостности внешних ключей (PRAGMA foreign_keys = ON)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("""
            INSERT INTO events (
                id, user_id, category_id, name, event_date, is_completed
            )
            VALUES (
                9999, 9999, 1, 'Некорректный пользователь', '2026-11-01', 0
            );
        """)

    conn.close()


def test_sql_queries_execution(tmp_path):
    test_db = tmp_path / "test_calendar.sqlite"
    import_all(test_db)
    conn = get_connection(test_db)

    # 1. WHERE
    active = conn.execute(
        "SELECT * FROM events WHERE is_completed = 0;"
    ).fetchall()
    assert len(active) > 0

    # 2. JOIN
    joined = conn.execute("""
        SELECT
            events.name,
            categories.name AS category_name,
            users.name AS user_name
        FROM events
        JOIN categories ON events.category_id = categories.id
        JOIN users ON events.user_id = users.id;
    """).fetchall()
    assert len(joined) > 0
    assert joined[0]["category_name"] is not None
    assert joined[0]["user_name"] is not None

    # 3. GROUP BY + LEFT JOIN
    cat_counts = conn.execute("""
        SELECT categories.name, COUNT(events.id) AS cnt
        FROM categories
        LEFT JOIN events ON categories.id = events.category_id
        GROUP BY categories.id, categories.name;
    """).fetchall()
    assert len(cat_counts) == 5

    # 4. GROUP BY + HAVING
    having_rows = conn.execute("""
        SELECT categories.name, COUNT(events.id) AS cnt
        FROM categories
        JOIN events ON categories.id = events.category_id
        GROUP BY categories.id, categories.name
        HAVING COUNT(events.id) > 1;
    """).fetchall()
    assert len(having_rows) > 0

    # 5. Подзапрос NOT IN
    free_users = conn.execute("""
        SELECT users.name
        FROM users
        WHERE users.id NOT IN (
            SELECT events.user_id FROM events
            WHERE events.event_date = '2026-10-20' AND events.is_completed = 0
        );
    """).fetchall()
    assert len(free_users) > 0

    conn.close()
