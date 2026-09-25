from datetime import date, datetime
from typing import Any

from models import DATE_FORMAT, Event


def parse_event_date(date_text: str) -> date:
    return datetime.strptime(date_text, DATE_FORMAT).date()


def add_event(events: list[Event], name: str, event_date: date) -> Event:
    if not name.strip():
        raise ValueError("Название события не может быть пустым.")
    event = Event(name=name.strip(), event_date=event_date)
    events.append(event)
    return event


def remove_event(events: list[Event], event_name: str) -> bool:
    for event in events:
        if event.name.casefold() == event_name.casefold():
            events.remove(event)
            return True
    return False


def sort_events(events: list[Event]) -> list[Event]:
    return sorted(
        events,
        key=lambda event: (event.event_date, event.name.casefold()),
    )


def event_status(event: Event, today: date | None = None) -> str:
    current_date = today or date.today()
    days_left = (event.event_date - current_date).days
    if days_left > 0:
        return f"До события осталось дней: {days_left}"
    if days_left == 0:
        return "Событие сегодня. Напоминание: не забудьте о нём!"
    return "Событие уже прошло."


def event_from_legacy_tuple(event_data: tuple[str, date]) -> Event:
    return Event(name=event_data[0], event_date=event_data[1])


def events_to_dict(events: list[Event]) -> list[dict[str, Any]]:
    return [event.to_dict() for event in events]


def events_from_dict(events_data: list[dict[str, Any]]) -> list[Event]:
    return [Event.from_dict(event_data) for event_data in events_data]
