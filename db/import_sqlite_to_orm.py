import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

# Определяем корневой каталог проекта.
# Скрипт находится в каталоге db, поэтому поднимаемся на уровень выше.
BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем корень проекта в пути поиска модулей Python.
sys.path.insert(0, str(BASE_DIR))

# Указываем путь к исходной базе данных (ПР7).
SOURCE_DB = BASE_DIR / "data" / "calendar.sqlite"

# Указываем модуль настроек Django.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "family_calendar.settings",
)

# Инициализируем Django после настройки пути и переменной окружения.
django.setup()

# Импортируем модели только после инициализации Django.
from categories.models import Category  # noqa: E402
from events.models import Event          # noqa: E402
from users.models import User            # noqa: E402


def main():
    # Проверяем, что исходная база существует.
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {SOURCE_DB}"
        )

    print(f"Чтение данных из исходной базы: {SOURCE_DB}")
    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row

        raw_categories = connection.execute(
            "SELECT id, name, description, icon FROM categories ORDER BY id;"
        ).fetchall()

        raw_users = connection.execute(
            "SELECT id, name, email FROM users ORDER BY id;"
        ).fetchall()

        raw_events = connection.execute(
            """
            SELECT id, user_id, category_id, name, event_date, is_completed
            FROM events
            ORDER BY id;
            """
        ).fetchall()

    print(f"Найдено в исходной базе: {len(raw_categories)} категорий, "
          f"{len(raw_users)} пользователей, {len(raw_events)} событий.")

    # Выполняем перенос в атомарной транзакции
    with transaction.atomic():
        # 1. Перенос категорий
        for cat in raw_categories:
            Category.objects.update_or_create(
                id=cat["id"],
                defaults={
                    "name": cat["name"],
                    "description": cat["description"] or "",
                    "icon": cat["icon"] or "📅",
                },
            )

        # 2. Перенос пользователей
        for usr in raw_users:
            User.objects.update_or_create(
                id=usr["id"],
                defaults={
                    "name": usr["name"],
                    "email": usr["email"],
                },
            )

        # 3. Перенос событий со связями
        for ev in raw_events:
            ev_date_raw = ev["event_date"]
            if isinstance(ev_date_raw, str):
                ev_date = date.fromisoformat(ev_date_raw)
            else:
                ev_date = ev_date_raw

            Event.objects.update_or_create(
                id=ev["id"],
                defaults={
                    "user_id": ev["user_id"],
                    "category_id": ev["category_id"],
                    "name": ev["name"],
                    "event_date": ev_date,
                    "is_completed": bool(ev["is_completed"]),
                },
            )

    print("\nПеренос данных в Django ORM успешно завершён:")
    print(f"  Категории: {Category.objects.count()}")
    print(f"  Пользователи: {User.objects.count()}")
    print(f"  События: {Event.objects.count()}")


if __name__ == "__main__":
    main()
