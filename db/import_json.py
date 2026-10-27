import json
from datetime import datetime
from pathlib import Path

try:
    from db.database import DB_PATH, get_connection, init_db
except ModuleNotFoundError:
    from database import DB_PATH, get_connection, init_db

BASE_DIR = Path(__file__).resolve().parent.parent
CATEGORIES_FILE = BASE_DIR / "data" / "categories.json"
USERS_FILE = BASE_DIR / "data" / "users.json"
EVENTS_FILE = BASE_DIR / "data" / "events.json"


def load_json(filepath):
    """Загрузить JSON-данные из файла."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_date(date_str):
    """Преобразовать дату в формат YYYY-MM-DD для SQL."""
    date_str = str(date_str).strip()
    if "-" in date_str:
        return date_str
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def import_categories(conn):
    """Импортировать категории в таблицу categories."""
    categories = load_json(CATEGORIES_FILE)
    conn.executemany(
        """
        INSERT OR REPLACE INTO categories (id, name, description, icon)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                cat["id"],
                cat["name"],
                cat.get("description", ""),
                cat.get("icon", "📅"),
            )
            for cat in categories
        ],
    )


def import_users(conn):
    """Импортировать пользователей в таблицу users."""
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT OR REPLACE INTO users (id, name, email)
        VALUES (?, ?, ?)
        """,
        [
            (
                user["id"],
                user["name"],
                user["email"],
            )
            for user in users
        ],
    )


def import_events(conn):
    """Импортировать события в таблицу events с привязкой по внешним ключам."""
    categories = conn.execute("SELECT id, name FROM categories").fetchall()
    cat_map = {row["name"].casefold(): row["id"] for row in categories}

    events_raw = load_json(EVENTS_FILE)
    rows_to_insert = []

    if isinstance(events_raw, dict) and "users" in events_raw:
        for user_entry in events_raw["users"]:
            user_id = user_entry["id"]
            for ev in user_entry.get("events", []):
                cat_id = cat_map.get(ev.get("category", "").casefold(), 1)
                rows_to_insert.append(
                    (
                        ev["id"],
                        user_id,
                        cat_id,
                        ev["name"],
                        normalize_date(ev["event_date"]),
                        1 if ev.get("is_completed") else 0,
                    )
                )

    # Дополнительные примеры событий для полноты выборки и статистики
    additional_events = [
        (6, 3, cat_map.get("здоровье и спорт", 4), "Тренировка в спортзале",
         "2026-10-22", 0),
        (7, 1, cat_map.get("учёба и работа", 2), "Подготовка отчета по ПР7",
         "2026-10-27", 0),
        (8, 2, cat_map.get("семья и дети", 3), "Поход в театр всей семьей",
         "2026-10-28", 0),
    ]

    existing_ids = {row[0] for row in rows_to_insert}
    for item in additional_events:
        if item[0] not in existing_ids:
            rows_to_insert.append(item)

    conn.executemany(
        """
        INSERT OR REPLACE INTO events (
            id,
            user_id,
            category_id,
            name,
            event_date,
            is_completed
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows_to_insert,
    )


def import_all(db_path=None):
    """Выполнить полный импорт данных в базу данных SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        import_categories(conn)
        import_users(conn)
        import_events(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    import_all(DB_PATH)
    print(f"Данные успешно импортированы в базу данных: {DB_PATH}")


if __name__ == "__main__":
    main()
