from datetime import date

import pytest

from calendar_service import (
    add_event,
    event_status,
    parse_event_date,
    remove_event,
    sort_events,
)
from models import Event
from storage import StorageError, load_events, save_events


def test_parse_event_date() -> None:
    assert parse_event_date("31.12.2099") == date(2099, 12, 31)


def test_parse_event_date_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        parse_event_date("31.02.2025")


def test_add_sort_and_remove_events() -> None:
    events: list[Event] = []
    add_event(events, "Новый год", date(2099, 1, 1))
    add_event(events, "День рождения", date(2080, 5, 10))

    assert [event.name for event in sort_events(events)] == [
        "День рождения",
        "Новый год",
    ]
    assert remove_event(events, "новый год") is True
    assert len(events) == 1


def test_event_status() -> None:
    event = Event("Встреча", date(2025, 1, 2))
    assert event_status(
        event,
        date(2025, 1, 1),
    ) == "До события осталось дней: 1"
    assert "сегодня" in event_status(event, date(2025, 1, 2))
    assert event_status(event, date(2025, 1, 3)) == "Событие уже прошло."


def test_json_round_trip(tmp_path) -> None:
    file_path = tmp_path / "events.json"
    source = {"Анна": [Event("Праздник", date(2026, 9, 8))]}
    save_events(file_path, source)

    assert load_events(file_path) == source


def test_invalid_json_raises_storage_error(tmp_path) -> None:
    file_path = tmp_path / "events.json"
    file_path.write_text("{broken", encoding="utf-8")

    with pytest.raises(StorageError):
        load_events(file_path)


def test_missing_file_returns_empty_storage(tmp_path) -> None:
    assert load_events(tmp_path / "missing.json") == {}


if __name__ == "__main__":
    pytest.main([__file__])
