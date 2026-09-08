from datetime import datetime

user_name = input("Введите имя пользователя: ")
events = []

while True:
    print()
    print("1 — добавить событие")
    print("2 — показать события")
    print("3 — сменить пользователя")
    print("4 — закрыть приложение")
    choice = input("Выберите действие: ")

    if choice == "4":
        break

    if choice == "3":
        user_name = input("Введите имя нового пользователя: ")
        events = []
        print("Пользователь изменён.")
        continue

    if choice == "2":
        print()
        print("События пользователя", user_name + ":")

        if len(events) == 0:
            print("Событий нет.")
        else:
            today = datetime.today().date()

            for event_name, event_date in events:
                days_left = (event_date - today).days
                print()
                print("Событие:", event_name)
                print("Дата:", event_date.strftime("%d.%m.%Y"))

                if days_left > 0:
                    print("До события осталось дней:", days_left)
                elif days_left == 0:
                    print("Событие сегодня. Напоминание: не забудьте о нём!")
                else:
                    print("Событие уже прошло.")

        input("Нажмите Enter, чтобы вернуться в меню...")
        continue

    if choice != "1":
        print("Неизвестная команда.")
        continue

    event_name = input("Введите название события: ")
    event_date_text = input("Введите дату события (ДД.ММ.ГГГГ): ")
    event_date = datetime.strptime(event_date_text, "%d.%m.%Y").date()
    events.append((event_name, event_date))
    print("Событие добавлено.")

print()
print("Приложение закрыто.")
