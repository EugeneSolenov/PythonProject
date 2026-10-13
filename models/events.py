from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

DATE_FORMAT = "%d.%m.%Y"


@dataclass
class Event:
    name: str
    event_date: date
    category: str = "общее"
    is_completed: bool = False
    id: int = 1

    def __str__(self) -> str:
        status = "выполнено" if self.is_completed else "актуально"
        return (
            f"{self.name} — {self.event_date.strftime(DATE_FORMAT)} "
            f"({self.category}, {status})"
        )

    def days_until(self, today: Optional[date] = None) -> int:
        current_date = today or date.today()
        return (self.event_date - current_date).days

    def is_upcoming(self, today: Optional[date] = None) -> bool:
        return self.days_until(today) >= 0 and not self.is_completed

    def mark_completed(self) -> None:
        self.is_completed = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
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
            id=int(data.get("id", 1)),
        )


def find_event_by_id(events: list[Event], event_id: int) -> Optional[Event]:
    """Найти событие по идентификатору."""
    for event in events:
        if event.id == event_id:
            return event
    return None


__all__ = ["DATE_FORMAT", "Event", "find_event_by_id"]
