import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "calendar.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(db_path=None):
    """Создать и вернуть настроенное подключение к SQLite."""
    target_path = Path(db_path) if db_path else DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None, schema_path=None):
    """Инициализировать схему базы данных из SQL-файла."""
    target_schema = Path(schema_path) if schema_path else SCHEMA_PATH
    conn = get_connection(db_path)
    try:
        with open(target_schema, "r", encoding="utf-8") as file:
            schema_sql = file.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"База данных успешно инициализирована: {DB_PATH}")
