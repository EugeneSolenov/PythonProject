import json
from pathlib import Path
from typing import Any

from models import Category, Event, User


class StorageError(Exception):
    pass


def load_users(file_path: str | Path = "data/events.json") -> list[User]:
    path = Path(file_path)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            raw_data: Any = json.load(file)
        if isinstance(raw_data, dict) and "users" in raw_data:
            raw_users = raw_data["users"]
        elif isinstance(raw_data, dict):
            raw_users = [
                {"id": index, "name": name, "events": events}
                for index, (name, events) in enumerate(raw_data.items(), 1)
            ]
        else:
            raw_users = raw_data
        return [User.from_dict(user_data) for user_data in raw_users]
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise StorageError(f"Не удалось загрузить данные: {path}") from error


def save_users(file_path: str | Path, users: list[User]) -> None:
    path = Path(file_path)
    data = {"users": [user.to_dict() for user in users]}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise StorageError(f"Не удалось сохранить данные: {path}") from error


def load_events(
    file_path: str | Path = "data/events.json",
) -> dict[str, list[Any]]:
    return {
        user.name: user.events
        for user in load_users(file_path)
    }


def save_events(
    file_path: str | Path,
    users_events: dict[str, list[Any]],
) -> None:
    users = [
        User(index, name, events)
        for index, (name, events) in enumerate(users_events.items(), 1)
    ]
    save_users(file_path, users)


def load_all_events(
    file_path: str | Path = "data/events.json",
) -> list[Event]:
    """Загрузить плоский список всех событий всех пользователей."""
    users = load_users(file_path)
    events: list[Event] = []
    current_id = 1
    for user in users:
        for event in user.events:
            if not getattr(event, "id", None) or event.id == 1:
                event.id = current_id
            current_id += 1
            events.append(event)
    return events


def load_categories(
    file_path: str | Path = "data/categories.json",
) -> list[Category]:
    """Загрузить список категорий."""
    path = Path(file_path)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return [Category.from_dict(item) for item in data]
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise StorageError(
            f"Не удалось загрузить категории: {path}"
        ) from error


def save_categories(
    file_path: str | Path,
    categories: list[Category],
) -> None:
    """Сохранить список категорий."""
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(
                [cat.to_dict() for cat in categories],
                file,
                ensure_ascii=False,
                indent=2,
            )
    except OSError as error:
        raise StorageError(
            f"Не удалось сохранить категории: {path}"
        ) from error


__all__ = [
    "StorageError",
    "load_all_events",
    "load_categories",
    "load_events",
    "load_users",
    "save_categories",
    "save_events",
    "save_users",
]
