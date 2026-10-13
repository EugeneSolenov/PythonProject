from datetime import date
from models.events import Event
from models.users import User


def test_user_properties() -> None:
    user = User(1, "Евгений", email="solenov@example.com")
    assert user.user_id == 1
    assert user.name == "Евгений"
    assert user.email == "solenov@example.com"
    assert "Евгений" in str(user)


def test_user_events_management() -> None:
    user = User(1, "Евгений")
    event = Event("Защита", date(2026, 10, 20), "учёба")
    user.add_event(event)

    assert len(user.events) == 1
    assert user.find_event("защита") is event
    assert user.find_event("неизвестно") is None

    assert user.remove_event("защита")
    assert len(user.events) == 0
