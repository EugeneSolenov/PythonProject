import sqlite3
from pathlib import Path

# Определяем корневой каталог проекта.
# Файл скрипта находится в подкаталоге db,
# поэтому родительский каталог на уровень выше — корень проекта.
BASE_DIR = Path(__file__).resolve().parent.parent

# Указываем путь к исходной базе, созданной на предыдущих работах.
SOURCE_DB = BASE_DIR / "data" / "calendar.sqlite"


def main():
    # Проверяем, что файл исходной базы существует.
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {SOURCE_DB}"
        )

    # Подключаемся к исходной базе SQLite.
    # Скрипт выполняет только запросы на чтение.
    with sqlite3.connect(SOURCE_DB) as connection:
        # Позволяем обращаться к значениям строк по именам столбцов.
        connection.row_factory = sqlite3.Row

        # Получаем список пользовательских таблиц базы данных.
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        ).fetchall()

        # Последовательно исследуем каждую таблицу.
        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")

            # Получаем описание столбцов таблицы:
            # имена, типы, признаки NULL, ключи и значения по умолчанию.
            columns = connection.execute(
                f'PRAGMA table_info("{table_name}");'
            ).fetchall()

            print("Столбцы:")
            for column in columns:
                print(
                    f"  имя={column['name']}, "
                    f"тип={column['type']}, "
                    f"NOT NULL={column['notnull']}, "
                    f"PRIMARY KEY={column['pk']}"
                )

            # Подсчитываем количество записей в таблице.
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}";'
            ).fetchone()[0]

            print(f"Количество записей: {count}")


if __name__ == "__main__":
    main()
