from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

DATE_FORMAT = "%d.%m.%Y"


@dataclass
class Event:
    name: str
    event_date: date
    category: str = "общее"
    is_completed: bool = False

    def __str__(self) -> str:
        status = "выполнено" if self.is_completed else "актуально"
        return (
            f"{self.name} — {self.event_date.strftime(DATE_FORMAT)} "
            f"({self.category}, {status})"
        )

    def days_until(self, today: date | None = None) -> int:
        current_date = today or date.today()
        return (self.event_date - current_date).days

    def is_upcoming(self, today: date | None = None) -> bool:
        return self.days_until(today) >= 0 and not self.is_completed

    def mark_completed(self) -> None:
        self.is_completed = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "event_date": self.event_date.strftime(DATE_FORMAT),
            "category": self.category,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        event_date_text = str(data["event_date"])
        if "-" in event_date_text:
            event_date = date.fromisoformat(event_date_text)
        else:
            event_date = datetime.strptime(event_date_text, DATE_FORMAT).date()
        return cls(
            name=str(data["name"]),
            event_date=event_date,
            category=str(data.get("category", "общее")),
            is_completed=bool(data.get("is_completed", False)),
        )


@dataclass
class User:
    user_id: int
    name: str
    events: list[Event] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} (событий: {len(self.events)})"

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def remove_event(self, event_name: str) -> bool:
        event = self.find_event(event_name)
        if event is None:
            return False
        self.events.remove(event)
        return True

    def find_event(self, event_name: str) -> Event | None:
        query = event_name.casefold()
        return next(
            (event for event in self.events if event.name.casefold() == query),
            None,
        )

    def upcoming_events(self, today: date | None = None) -> list[Event]:
        return [event for event in self.events if event.is_upcoming(today)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.user_id,
            "name": self.name,
            "events": [event.to_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        events = [Event.from_dict(item) for item in data.get("events", [])]
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            events=events,
        )


__all__ = ["DATE_FORMAT", "Event", "User"]
