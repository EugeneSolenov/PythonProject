from dataclasses import dataclass, field
from typing import Any, Optional
from .events import Event


@dataclass
class User:
    user_id: int
    name: str
    events: list[Event] = field(default_factory=list)
    email: str = ""

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

    def find_event(self, event_name: str) -> Optional[Event]:
        query = event_name.casefold()
        return next(
            (event for event in self.events if event.name.casefold() == query),
            None,
        )

    def upcoming_events(self, today: Any = None) -> list[Event]:
        return [event for event in self.events if event.is_upcoming(today)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.user_id,
            "name": self.name,
            "email": self.email,
            "events": [event.to_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        events = [Event.from_dict(item) for item in data.get("events", [])]
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            email=str(data.get("email", "")),
            events=events,
        )


__all__ = ["User"]
