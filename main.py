from datetime import date
from pathlib import Path

from calendar_service import (
    add_event as add_event_to_user,
    event_status,
    parse_event_date,
    remove_event,
    sort_events,
)
from models import Event, User
from storage import StorageError, load_users, save_users

DATA_FILE = Path("data/events.json")


def add_event(events: list[tuple[str, date]]) -> None:
    name = input("Введите название события: ")
    date_text = input("Введите дату события (ДД.ММ.ГГГГ): ")
    events.append((name, parse_event_date(date_text)))
    print("Событие добавлено.")


def show_events(
    user_or_name: User | str,
    events: list[Event] | list[tuple[str, date]] | None = None,
) -> None:
    if isinstance(user_or_name, User):
        user_name = user_or_name.name
        user_events = user_or_name.events
    else:
        user_name = user_or_name
        user_events = [
            Event(name, event_date)
            for name, event_date in events or []
        ]
    print()
    print("События пользователя", user_name + ":")
    if not user_events:
        print("Событий нет.")
    else:
        for event in sort_events(user_events):
            print()
            print("Событие:", event.name)
            print("Дата:", event.event_date.strftime("%d.%m.%Y"))
            print("Категория:", event.category)
            print(event_status(event))
    input("Нажмите Enter, чтобы вернуться в меню...")


def create_event(user: User) -> None:
    name = input("Введите название события: ")
    date_text = input("Введите дату события (ДД.ММ.ГГГГ): ")
    category = input("Введите категорию события: ")
    add_event_to_user(user, name, parse_event_date(date_text), category)
    print("Событие добавлено.")


def print_menu() -> None:
    print()
    print("1 — добавить событие")
    print("2 — показать события")
    print("3 — удалить событие")
    print("4 — отметить событие выполненным")
    print("5 — сменить пользователя")
    print("6 — закрыть приложение")


def find_or_create_user(users: list[User], name: str) -> User:
    for user in users:
        if user.name.casefold() == name.casefold():
            return user
    user = User(len(users) + 1, name)
    users.append(user)
    return user


def main() -> None:
    try:
        users = load_users(DATA_FILE)
    except StorageError as error:
        print(error)
        users = []

    user_name = input("Введите имя пользователя: ").strip()
    user = find_or_create_user(users, user_name)

    while True:
        print_menu()
        choice = input("Выберите действие: ")
        if choice == "6":
            break
        if choice == "5":
            name = input("Введите имя нового пользователя: ").strip()
            user = find_or_create_user(users, name)
        elif choice == "4":
            name = input("Введите название события: ")
            event = user.find_event(name)
            if event is None:
                print("Событие не найдено.")
            else:
                event.mark_completed()
                print("Событие отмечено как выполненное.")
        elif choice == "3":
            name = input("Введите название события для удаления: ")
            message = (
                "Событие удалено."
                if remove_event(user, name)
                else "Событие не найдено."
            )
            print(message)
        elif choice == "2":
            show_events(user)
        elif choice == "1":
            try:
                create_event(user)
            except ValueError:
                print("Ошибка: дата должна быть в формате ДД.ММ.ГГГГ.")
        else:
            print("Неизвестная команда.")
        try:
            save_users(DATA_FILE, users)
        except StorageError as error:
            print(error)

    save_users(DATA_FILE, users)
    print("Приложение закрыто.")


if __name__ == "__main__":
    main()


__all__ = ["add_event", "main", "show_events"]
