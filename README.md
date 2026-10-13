# Семейный календарь — Веб-приложение на Django (ПР5 и ПР6)

Индивидуальный сквозной учебный проект по дисциплине «Технологии разработки приложений на базе фреймворков».
Проект представляет собой менеджер персональных и семейных событий, напоминаний и памятных дат с консольным интерфейсом (ПР1–ПР3) и веб-интерфейсом на базе Django (ПР5 и ПР6).

---

## 1. Назначение проекта

«Семейный календарь» — приложение для учёта важных дат, семейных праздников, учебных дедлайнов и повседневных дел нескольких пользователей.
Проект развивается поэтапно:
- **ПР1–ПР3**: консольное приложение, модульная структура, объектная модель (`Event`, `User`), хранение данных в JSON, автоматические тесты;
- **ПР5**: добавление веб-слоя на Django: HTTP-запросы/ответы, трехуровневая маршрутизация URL, view-функции, обработка ошибок 404, подключение Bootstrap;
- **ПР6**: полноценный перевод веб-интерфейса на **Django Template Language (DTL)**: базовый шаблон, наследование, включаемые компоненты (`{% include %}`), пространства имён URL, фильтры шаблонов, передача контекста, собственные статические файлы (CSS, JS, логотип).

---

## 2. Используемые технологии

- **Python 3.14**
- **Django 5.2**
- **Django Template Language (DTL)**
- **HTML5 & CSS3**
- **Bootstrap 5.3** (через CDN)
- **JavaScript** (клиентская динамика)
- **JSON** (файловое хранилище)
- **pytest** (автоматизированное тестирование)
- **flake8** (статический анализ и проверка PEP 8)
- **Git** (контроль версий)

---

## 3. Предметная область и сущности

В проекте используются ключевые сущности предметной области (пакет `models/`):

1. **`Event` (Событие)**:
   - Атрибуты: `id`, `name` (название), `event_date` (дата), `category` (категория), `is_completed` (статус выполнения).
   - Методы: `days_until()` (число дней до события), `is_upcoming()` (проверка актуальности), `mark_completed()` (отметка выполнения), `to_dict()` и `from_dict()` (сериализация JSON).
   - Поиск: `find_event_by_id()`.

2. **`User` (Пользователь / Член семьи)**:
   - Атрибуты: `user_id`, `name`, `email`, `events: list[Event]`.
   - Методы: `add_event()`, `remove_event()`, `find_event()`, `upcoming_events()`, `to_dict()`, `from_dict()`.

3. **`Category` (Категория событий)**:
   - Атрибуты: `id`, `name`, `description`, `icon`.
   - Методы: `to_dict()`, `from_dict()`, `find_category_by_id()`.

> [!NOTE]
> На текущем этапе (ПР5–ПР6) данные хранятся в JSON-файлах (`data/events.json`, `data/categories.json`), а доступ к ним организован через модуль `storage.py`. Переход к Django ORM и реляционной базе данных запланирован на следующие практические работы.

---

## 4. Структура проекта

```text
PythonProject/
├── manage.py                          # Точка входа для команд управления Django
├── requirements.txt                   # Зависимости проекта
├── README.md                          # Документация проекта
├── main.py                            # Консольный интерфейс приложения (ПР1–ПР3)
├── calendar_service.py                # Бизнес-логика обработки событий
├── storage.py                         # Модуль сохранения и загрузки JSON-данных
├── create_reports.py                  # Скрипт генерации отчётов по практическим работам
│
├── family_calendar/                   # Пакет конфигурации Django-проекта
│   ├── __init__.py
│   ├── settings.py                    # Настройки проекта (INSTALLED_APPS, TEMPLATES, и др.)
│   ├── urls.py                        # Корневая маршрутизация и handler404
│   ├── asgi.py
│   └── wsgi.py
│
├── homepage/                          # Django-приложение: Главная страница
│   ├── apps.py
│   ├── views.py                       # index (главная), page_not_found (404)
│   ├── urls.py                        # namespace 'homepage'
│   ├── templates/homepage/
│   │   └── index.html                 # Главная страница (сводка, метрики)
│   └── static/homepage/
│       ├── css/style.css              # Собственные стили проекта
│       ├── js/main.js                 # Клиентский скрипт (динамический год)
│       └── img/logo.png               # Логотип Семейного календаря
│
├── events/                            # Django-приложение: События календаря
│   ├── apps.py
│   ├── views.py                       # events (список), event_detail (детальная страница)
│   ├── urls.py                        # namespace 'events', динамический URL <int:event_id>/
│   └── templates/events/
│       ├── event_list.html            # Список событий (фильтр length, цикл, empty)
│       ├── event_detail.html          # Детальная карточка события (условие if/else)
│       └── includes/
│           ├── event_card.html        # Компонент карточки (фильтр default)
│           └── event_status.html      # Компонент цветного бейджа статуса
│
├── categories/                        # Django-приложение: Категории событий
│   ├── apps.py
│   ├── views.py                       # categories (список), category_detail (детали)
│   ├── urls.py                        # namespace 'categories', <int:category_id>/
│   └── templates/categories/
│       ├── category_list.html         # Список категорий
│       ├── category_detail.html       # Категория и события в ней
│       └── includes/
│           └── category_card.html     # Карточка категории
│
├── templates/                         # Шаблоны уровня проекта
│   ├── base.html                      # Базовый каркас сайта (extends, blocks)
│   ├── 404.html                       # Кастомная страница ошибки 404
│   └── includes/
│       └── navigation.html            # Единая навигационная панель ({% url %})
│
├── models/                            # Пакет классов предметной области
│   ├── __init__.py
│   ├── events.py                      # Класс Event и find_event_by_id
│   ├── users.py                       # Класс User
│   └── categories.py                  # Класс Category и find_category_by_id
│
├── data/                              # Файловые хранилища данных
│   ├── events.json                    # События и пользователи
│   └── categories.json                # Категории событий
│
└── tests/                             # Автоматизированные тесты
    ├── test_calendar.py               # Тесты методов Event и User
    ├── test_categories.py             # Тесты Category
    ├── test_users.py                  # Тесты работы с пользователями
    ├── test_views.py                  # Тесты Django view, роутинга и шаблонов
    └── test_main.py                   # Тесты консольного сценария
```

---

## 5. Возможности веб-интерфейса и реализация DTL

Веб-интерфейс полностью построен на системе шаблонов **Django Template Language (DTL)**:

1. **Базовый шаблон (`templates/base.html`)**:
   - Единая разметка HTML5, мета-теги, подключение Bootstrap 5.3 и собственных статических файлов (`style.css`, `main.js`, `logo.png`).
   - Блоки для дочерних страниц: `{% block title %}` и `{% block content %}`.

2. **Наследование (`{% extends %}`)**:
   - Все страницы приложений наследуют `base.html` без дублирования HTML-каркаса.

3. **Включаемые шаблоны (`{% include %}`)**:
   - `templates/includes/navigation.html` — общая навигация сайта;
   - `events/includes/event_card.html` — карточка события;
   - `events/includes/event_status.html` — статус выполнения события;
   - `categories/includes/category_card.html` — карточка категории.

4. **Именованные URL и пространства имён (Namespaces)**:
   - В ссылках исключены жёстко заданные адреса; используются вызовы `{% url %}`:
     - `homepage:index` — главная страница (`/`);
     - `events:list` — список всех событий (`/events/`);
     - `events:detail event.id` — страница конкретного события (`/events/<int:event_id>/`);
     - `categories:list` — список категорий (`/categories/`);
     - `categories:detail cat.id` — детальная страница категории (`/categories/<int:category_id>/`).

5. **Фильтры шаблонов**:
   - `{{ events|length }}` — количество элементов в списке;
   - `{{ event.name|default:"Без названия" }}` — значение по умолчанию при отсутствии имени.

6. **Условия и циклы**:
   - `{% for event in events %} ... {% empty %} ... {% endfor %}` — аккуратный вывод коллекций и обработка пустых списков;
   - `{% if event.is_completed %} ... {% else %} ... {% endif %}` — условное отображение статусов и данных.

7. **Обработка ошибки 404 (Not Found)**:
   - Корневой обработчик `handler404 = "homepage.views.page_not_found"`;
   - При обращении к несуществующему объекту (`/events/9999/` или `/categories/9999/`) возвращается HTTP-ответ со статусом `404` и понятной пользователю страницей.

8. **Статические файлы (`{% load static %}`)**:
   - `homepage/css/style.css` — собственное оформление карточек, логотипа и бейджей;
   - `homepage/js/main.js` — клиентский скрипт (динамическая установка актуального года в футере);
   - `homepage/img/logo.png` — графический логотип приложения.

---

## 6. Запуск и проверка проекта

### Запуск веб-сервера Django:
```bash
python manage.py runserver
```
Веб-интерфейс доступен в браузере по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Запуск консольной версии (ПР1–ПР3):
```bash
python main.py
```

### Проверка конфигурации Django:
```bash
python manage.py check
```

### Запуск автоматических тестов (pytest):
```bash
python -m pytest -v
```
Все 25 тестов (консольный сценарий, модели предметной области, хранилище, Django view-функции и шаблоны) выполняются успешно.

### Проверка стиля кода (flake8):
```bash
flake8 . --extend-exclude=venv
```
Код полностью соответствует стандарту PEP 8 (без предупреждений и ошибок).
