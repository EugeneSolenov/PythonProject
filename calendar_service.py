from datetime import date, datetime
from typing import Any

from models import DATE_FORMAT, Event, User


def parse_event_date(date_text: str) -> date:
    return datetime.strptime(date_text, DATE_FORMAT).date()


def add_event(
    user: User,
    name: str,
    event_date: date,
    category: str = "общее",
) -> Event:
    if not name.strip():
        raise ValueError("Название события не может быть пустым.")
    event = Event(name.strip(), event_date, category.strip() or "общее")
    user.add_event(event)
    return event


def remove_event(user: User, event_name: str) -> bool:
    return user.remove_event(event_name)


def sort_events(events: list[Event]) -> list[Event]:
    return sorted(
        events,
        key=lambda event: (event.event_date, event.name.casefold()),
    )


def event_status(event: Event, today: date | None = None) -> str:
    if event.is_completed:
        return "Событие выполнено."
    days_left = event.days_until(today)
    if days_left > 0:
        return f"До события осталось дней: {days_left}"
    if days_left == 0:
        return "Событие сегодня. Напоминание: не забудьте о нём!"
    return "Событие уже прошло."


def events_to_dict(events: list[Event]) -> list[dict[str, Any]]:
    return [event.to_dict() for event in events]


def events_from_dict(events_data: list[dict[str, Any]]) -> list[Event]:
    return [Event.from_dict(event_data) for event_data in events_data]


__all__ = [
    "add_event",
    "event_status",
    "events_from_dict",
    "events_to_dict",
    "parse_event_date",
    "remove_event",
    "sort_events",
]
