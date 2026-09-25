import json
from pathlib import Path
from typing import Any

from calendar_service import events_from_dict, events_to_dict
from models import Event


class StorageError(Exception):
    pass


def load_events(file_path: str | Path) -> dict[str, list[Event]]:
    path = Path(file_path)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            raw_data: dict[str, list[dict[str, Any]]] = json.load(file)
        return {
            user_name: events_from_dict(events_data)
            for user_name, events_data in raw_data.items()
        }
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise StorageError(f"Не удалось загрузить данные: {path}") from error


def save_events(
    file_path: str | Path,
    users_events: dict[str, list[Event]],
) -> None:
    path = Path(file_path)
    raw_data = {
        user_name: events_to_dict(events)
        for user_name, events in users_events.items()
    }
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(raw_data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise StorageError(f"Не удалось сохранить данные: {path}") from error


def create_empty_storage(file_path: str | Path) -> None:
    path = Path(file_path)
    if not path.exists():
        save_events(path, {})


__all__ = [
    "StorageError",
    "create_empty_storage",
    "load_events",
    "save_events",
]
