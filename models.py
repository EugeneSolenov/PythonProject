from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

DATE_FORMAT = "%d.%m.%Y"


@dataclass
class Event:
    name: str
    event_date: date

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["event_date"] = self.event_date.strftime(DATE_FORMAT)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        event_date_text = str(data["event_date"])
        if "-" in event_date_text:
            event_date = date.fromisoformat(event_date_text)
        else:
            event_date = datetime.strptime(event_date_text, DATE_FORMAT).date()
        return cls(name=str(data["name"]), event_date=event_date)
