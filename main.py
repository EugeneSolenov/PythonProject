from datetime import date
from pathlib import Path

from calendar_service import (
    add_event as add_event_to_collection,
    event_from_legacy_tuple,
    event_status,
    parse_event_date,
    remove_event,
    sort_events,
)
from models import Event
from storage import StorageError, load_events, save_events

DATA_FILE = Path("data/events.json")


def add_event(events: list[tuple[str, date]]) -> None:
    event_name = input("Введите название события: ")
    event_date_text = input("Введите дату события (ДД.ММ.ГГГГ): ")
    event_date = parse_event_date(event_date_text)
    events.append((event_name, event_date))
    print("Событие добавлено.")


def prompt_and_add_event(events: list[Event]) -> None:
    event_name = input("Введите название события: ")
    event_date_text = input("Введите дату события (ДД.ММ.ГГГГ): ")
    event_date = parse_event_date(event_date_text)
    add_event_to_collection(events, event_name, event_date)
    print("Событие добавлено.")


def show_events(
    user_name: str,
    events: list[Event] | list[tuple[str, date]],
) -> None:
    print()
    print("События пользователя", user_name + ":")
    if not events:
        print("Событий нет.")
    else:
        normalized_events = (
            [event_from_legacy_tuple(event) for event in events]
            if isinstance(events[0], tuple)
            else events
        )
        for event in sort_events(normalized_events):
            print()
            print("Событие:", event.name)
            print("Дата:", event.event_date.strftime("%d.%m.%Y"))
            print(event_status(event))
    input("Нажмите Enter, чтобы вернуться в меню...")


def print_menu() -> None:
    print()
    print("1 — добавить событие")
    print("2 — показать события")
    print("3 — удалить событие")
    print("4 — сменить пользователя")
    print("5 — закрыть приложение")


def main() -> None:
    try:
        users_events = load_events(DATA_FILE)
    except StorageError as error:
        print(error)
        users_events = {}

    user_name = input("Введите имя пользователя: ").strip()
    users_events.setdefault(user_name, [])

    while True:
        print_menu()
        choice = input("Выберите действие: ")
        current_events = users_events[user_name]

        if choice == "5":
            break
        if choice == "4":
            user_name = input("Введите имя нового пользователя: ").strip()
            users_events.setdefault(user_name, [])
            print("Пользователь изменён.")
        elif choice == "3":
            event_name = input("Введите название события для удаления: ")
            if remove_event(current_events, event_name):
                print("Событие удалено.")
            else:
                print("Событие не найдено.")
        elif choice == "2":
            show_events(user_name, current_events)
        elif choice == "1":
            try:
                prompt_and_add_event(current_events)
            except ValueError:
                print("Ошибка: дата должна быть в формате ДД.ММ.ГГГГ.")
        else:
            print("Неизвестная команда.")

        try:
            save_events(DATA_FILE, users_events)
        except StorageError as error:
            print(error)

    print()
    print("Приложение закрыто.")


if __name__ == "__main__":
    main()
