from datetime import date

import pytest

from calendar_service import (
    add_event,
    event_status,
    parse_event_date,
    remove_event,
    sort_events,
)
from models import Event, User
from storage import StorageError, load_users, save_users


def test_event_object() -> None:
    event = Event("День рождения", date(2099, 12, 31), "личное")
    assert event.name == "День рождения"
    assert event.days_until(date(2099, 12, 30)) == 1
    assert event.is_upcoming(date(2099, 12, 30))
    assert "День рождения" in str(event)


def test_event_completion() -> None:
    event = Event("Встреча", date(2099, 1, 1))
    event.mark_completed()
    assert event.is_completed
    assert not event.is_upcoming(date(2098, 1, 1))


def test_user_manages_events() -> None:
    user = User(1, "Анна")
    event = add_event(user, "Праздник", date(2099, 5, 10))
    assert user.find_event("праздник") is event
    assert user.upcoming_events(date(2099, 1, 1)) == [event]
    assert remove_event(user, "ПРАЗДНИК")
    assert user.events == []


def test_sort_events() -> None:
    events = [
        Event("Позднее", date(2099, 12, 31)),
        Event("Ранее", date(2099, 1, 1)),
    ]
    assert [event.name for event in sort_events(events)] == [
        "Ранее",
        "Позднее",
    ]


def test_status_and_date_validation() -> None:
    event = Event("Встреча", date(2025, 1, 2))
    assert event_status(
        event,
        date(2025, 1, 1),
    ) == "До события осталось дней: 1"
    with pytest.raises(ValueError):
        parse_event_date("31.02.2025")


def test_json_round_trip(tmp_path) -> None:
    path = tmp_path / "events.json"
    users = [User(1, "Анна", [Event("Праздник", date(2026, 9, 8), "семья")])]
    save_users(path, users)
    loaded = load_users(path)
    assert loaded[0].name == "Анна"
    assert loaded[0].events[0].category == "семья"
    assert loaded[0].events[0].event_date == date(2026, 9, 8)


def test_invalid_json_raises_storage_error(tmp_path) -> None:
    path = tmp_path / "events.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(StorageError):
        load_users(path)


def test_missing_file_returns_empty_list(tmp_path) -> None:
    assert load_users(tmp_path / "missing.json") == []


if __name__ == "__main__":
    pytest.main([__file__])
