from datetime import date

import pytest

from main import add_event, show_events


def test_add_event(monkeypatch):
    answers = iter(["День рождения", "31.12.2099"])
    events = []

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    add_event(events)

    assert events == [("День рождения", date(2099, 12, 31))]


def test_add_event_uses_date_format(monkeypatch):
    answers = iter(["Новый год", "01.01.2020"])
    events = []

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    add_event(events)

    assert events[0][1].strftime("%d.%m.%Y") == "01.01.2020"


def test_show_events_when_list_is_empty(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "")

    show_events("Анна", [])

    output = capsys.readouterr().out

    assert "События пользователя Анна:" in output
    assert "Событий нет." in output


def test_show_events_prints_event(monkeypatch, capsys):
    events = [("День рождения", date(2099, 12, 31))]
    monkeypatch.setattr("builtins.input", lambda _: "")

    show_events("Анна", events)

    output = capsys.readouterr().out

    assert "Событие: День рождения" in output
    assert "Дата: 31.12.2099" in output
    assert "До события осталось дней:" in output


def test_add_event_rejects_invalid_date(monkeypatch):
    answers = iter(["Встреча", "31.02.2025"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    with pytest.raises(ValueError):
        add_event([])
