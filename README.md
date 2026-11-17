# Семейный календарь — Веб-приложение на Django (ПР5, ПР6, ПР7, ПР9)

Индивидуальный сквозной учебный проект по дисциплине «Технологии разработки приложений на базе фреймворков».
Проект представляет собой менеджер персональных и семейных событий, напоминаний и памятных дат с консольным интерфейсом (ПР1–ПР3), веб-интерфейсом на базе Django с шаблонами DTL (ПР5 и ПР6), слоем реляционной базы данных SQLite с SQL-запросами (ПР7) и современным объектно-реляционным слоем на базе **Django ORM** (ПР9).

---

## 1. Назначение проекта

«Семейный календарь» — приложение для учёта важных дат, семейных праздников, учебных дедлайнов и повседневных дел нескольких пользователей.
Проект развивается поэтапно:
- **ПР1–ПР3**: консольное приложение, модульная структура, объектная модель (`Event`, `User`), хранение данных в JSON, автоматические тесты;
- **ПР5**: добавление веб-слоя на Django: HTTP-запросы/ответы, трехуровневая маршрутизация URL, view-функции, обработка ошибок 404, подключение Bootstrap;
- **ПР6**: полноценный перевод веб-интерфейса на **Django Template Language (DTL)**: базовый шаблон, наследование, включаемые компоненты (`{% include %}`), пространства имён URL, фильтры шаблонов, передача контекста, собственные статические файлы (CSS, JS, логотип);
- **ПР7**: внедрение слоя реляционной базы данных **SQLite**: проектирование таблиц, первичных и внешних ключей (`FOREIGN KEY`), модуль подключения `db/database.py` с контролем ссылочной целостности (`PRAGMA foreign_keys = ON`), скрипт импорта данных `db/import_json.py`, разработка 12 SQL-запросов (`sql/queries.sql`), параметризованный поиск по дате и страница статистики на основе SQL-агрегатов и группировок;
- **ПР9**: переход слоя доступа к данным на **Django ORM**: разработка моделей `Category`, `User`, `Event`, настройка связей `ForeignKey`, `on_delete` и `related_name`, управление схемой базы данных через миграции Django, миграция данных из SQLite ПР7 (`db/import_sqlite_to_orm.py`), перевод представлений на QuerySet API, многокритериальная фильтрация, исключение записей (`exclude`), поиск по нескольким полям через `Q`-объекты, сортировка с валидацией, агрегация и аннотирование (`aggregate`, `annotate`), постраничная навигация (`Paginator`) с сохранением GET-параметров в шаблонах через `{% querystring %}`.

---

## 2. Используемые технологии

- **Python 3.14**
- **Django 5.2**
- **Django ORM** (объектно-реляционное отображение, QuerySet, Q-объекты, агрегаты, Paginator)
- **Миграции Django** (`makemigrations`, `migrate`, `sqlmigrate`, `showmigrations`)
- **SQLite 3 & SQL** (реляционное хранение данных в `db.sqlite3` и `data/calendar.sqlite`)
- **sqlite3** (стандартная библиотека Python, `sqlite3.Row` — слой ПР7 сохранён для преемственности)
- **Django Template Language (DTL)**
- **HTML5 & CSS3**
- **Bootstrap 5.3** (через CDN)
- **JavaScript** (клиентская динамика)
- **JSON** (файловое хранилище для начальной миграции данных)
- **pytest** (автоматизированное тестирование)
- **flake8** (статический анализ и проверка PEP 8)
- **Git** (контроль версий)

---

## 3. Слой доступа к данным через Django ORM (ПР9)

### 3.1. Модели данных проекта

Модели данных размещены в модулях `models.py` соответствующих Django-приложений:

1. **Модель `Category` (`categories/models.py`)**:
   - `name` — `models.CharField(max_length=100, unique=True, verbose_name="Название")`
   - `description` — `models.TextField(blank=True, default="", verbose_name="Описание")`
   - `icon` — `models.CharField(max_length=10, default="📅", verbose_name="Иконка / эмодзи")`
   - `Meta` — `ordering = ["name"]`, verbose-имена в единственном и множественном числе.

2. **Модель `User` (`users/models.py`)**:
   - `name` — `models.CharField(max_length=100, verbose_name="Имя")`
   - `email` — `models.EmailField(unique=True, verbose_name="Электронная почта")`
   - `Meta` — `ordering = ["name"]`, verbose-имена.

3. **Модель `Event` (`events/models.py`)**:
   - `name` — `models.CharField(max_length=200, verbose_name="Название события")`
   - `event_date` — `models.DateField(verbose_name="Дата события")`
   - `is_completed` — `models.BooleanField(default=False, verbose_name="Выполнено")`
   - `user` — `models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", verbose_name="Ответственный пользователь")`
   - `category` — `models.ForeignKey(Category, on_delete=models.PROTECT, related_name="events", verbose_name="Категория")`
   - Методы: `complete()`, `mark_completed()`, `days_until()`, `is_upcoming()`, строковое представление `__str__()`.
   - Свойства: `category_icon`, `user_name`, `user_email` (для бесшовной совместимости с шаблонами DTL).

### 3.2. Настройка связей и ссылочной целостности

- **`Event -> User`**: `models.ForeignKey` с `on_delete=models.CASCADE`. При удалении пользователя удаляются связанные с ним события.
- **`Event -> Category`**: `models.ForeignKey` с `on_delete=models.PROTECT`. Запрещено удалять категорию, пока к ней привязано хотя бы одно событие (защита ссылочной целостности).
- **`related_name="events"`**: обеспечивает доступ к обратным связям (`category.events.all()`, `user.events.all()`).

### 3.3. Миграции и перенос данных

1. Структура базы данных формируется и управляется штатными миграциями:
   - `categories/migrations/0001_initial.py`
   - `users/migrations/0001_initial.py`
   - `events/migrations/0001_initial.py`
2. Перенос данных из предыдущей базы `data/calendar.sqlite` (ПР7) в ORM (`db.sqlite3`) выполняется скриптом `db/import_sqlite_to_orm.py`:
   - Создана резервная копия `data/calendar_backup.sqlite`.
   - Данные 5 категорий, 3 пользователей и 8 событий перенесены с полным сохранением связей и первичных ключей.

### 3.4. Реализованные операции Django ORM (более 15 выражений)

1. `Category.objects.all()` / `Event.objects.all()` — выборка наборов объектов.
2. `Event.objects.get(id=...)` — получение одного объекта по первичному ключу.
3. `get_object_or_404(Category, id=...)` — безопасное получение объекта с обработкой 404.
4. `Event.objects.filter(event_date=...)` — точная фильтрация по дате.
5. `Event.objects.filter(category_id=...)` — фильтрация по внешнему ключу.
6. `Event.objects.filter(user_id=...)` — фильтрация по ответственному пользователю.
7. `Event.objects.filter(is_completed=...)` — фильтрация по статусу выполнения.
8. `Event.objects.exclude(is_completed=True)` — исключение выполненных событий.
9. `Event.objects.filter(user__name__icontains=...)` — фильтрация по полю связанной модели.
10. `Event.objects.filter(Q(name__icontains=q) | Q(category__name__icontains=q) | Q(user__name__icontains=q))` — сложный поиск по нескольким полям с логическим «ИЛИ».
11. `Event.objects.order_by("event_date")` / `order_by("-event_date")` — сортировка по возрастанию и убыванию.
12. `Event.objects.select_related("category", "user")` — оптимизация SQL-запросов через единый JOIN.
13. `Event.objects.values("id", "name", "event_date", "is_completed")` — выборка сокращённого набора полей в виде словарей.
14. `Event.objects.aggregate(total=Count("id"), min_date=Min("event_date"), max_date=Max("event_date"))` — вычисление сводных агрегатов.
15. `Category.objects.annotate(events_count=Count("events"))` — аннотирование категорий количеством привязанных событий.
16. `User.objects.annotate(events_count=Count("events"))` — аннотирование пользователей количеством событий.
17. `Paginator(events_qs, 5)` — постраничный вывод с разбивкой QuerySet на страницы.

---

## 4. Слой реляционной базы данных ПР7 (сохранён для преемственности)

Для обеспечения преемственности и работы модулей ПР1–ПР7 в репозитории сохранены:
- **`sql/schema.sql`** — исходная DDL-схема таблиц SQLite;
- **`sql/queries.sql`** — 12 SQL-запросов (WHERE, JOIN, GROUP BY, HAVING, подзапросы);
- **`db/database.py`** — низкоуровневый модуль подключения с `PRAGMA foreign_keys = ON`;
- **`db/import_json.py`** — скрипт импорта из JSON в `data/calendar.sqlite`;
- **`db/inspect_source_db.py`** — скрипт инспекции структуры и строк исходной БД;
- **`db/import_sqlite_to_orm.py`** — скрипт переноса данных из `data/calendar.sqlite` в `db.sqlite3`.

---

## 5. Структура проекта

```text
PythonProject/
├── manage.py                          # Точка входа для команд управления Django
├── requirements.txt                   # Зависимости проекта
├── README.md                          # Документация проекта (ПР9)
├── pytest.ini                         # Конфигурация для запуска тестов pytest
├── .flake8                            # Конфигурация статического анализатора flake8
├── db.sqlite3                         # База данных Django ORM (ПР9)
│
├── sql/                               # SQL-скрипты проекта (ПР7)
│   ├── schema.sql                     # Схема создания таблиц и внешних ключей
│   └── queries.sql                    # 12 аналитических и рабочих SQL-запросов
│
├── db/                                # Модули работы с базами данных
│   ├── __init__.py
│   ├── database.py                    # Фабрика подключений SQLite (ПР7)
│   ├── import_json.py                 # Скрипт миграции JSON -> data/calendar.sqlite
│   ├── inspect_source_db.py           # Инспекция таблиц исходной БД SQLite (ПР9)
│   └── import_sqlite_to_orm.py        # Перенос данных SQLite -> Django ORM (ПР9)
│
├── data/                              # Хранилище данных
│   ├── categories.json                # Исходный JSON категорий
│   ├── users.json                     # Исходный JSON пользователей
│   ├── events.json                    # Исходный JSON событий
│   ├── calendar.sqlite                # Исходная БД SQLite (ПР7)
│   └── calendar_backup.sqlite         # Резервная копия БД (ПР9)
│
├── family_calendar/                   # Пакет конфигурации Django-проекта
│   ├── __init__.py
│   ├── settings.py                    # Настройки (INSTALLED_APPS: users, events, categories)
│   ├── urls.py                        # Корневая маршрутизация и handler404
│   ├── asgi.py
│   └── wsgi.py
│
├── homepage/                          # Django-приложение: Главная страница
│   ├── views.py                       # index (сводка метрик через ORM), page_not_found (404)
│   ├── urls.py                        # namespace 'homepage'
│   ├── templates/homepage/index.html  # Главная страница (метрики ORM, ближайшие события)
│   └── static/homepage/
│       ├── css/style.css              # Собственные стили проекта
│       ├── js/main.js                 # Клиентский скрипт (динамический год)
│       └── img/logo.png               # Логотип Семейного календаря
│
├── events/                            # Django-приложение: События календаря (ПР9 ORM)
│   ├── models.py                      # Модель Event (user, category, dates, status, methods)
│   ├── views.py                       # events (фильтры, сортировка, пагинация), event_detail,
│   │                                  # search_events (Q-поиск), statistics (aggregate/annotate)
│   ├── urls.py                        # namespace 'events'
│   ├── migrations/
│   │   └── 0001_initial.py            # Начальная миграция модели Event
│   └── templates/events/
│       ├── event_list.html            # Список событий с формой фильтров, сортировкой и пагинацией
│       ├── event_detail.html          # Детальная карточка события через ORM-связи
│       ├── search.html                # Форма поиска по тексту и дате
│       ├── statistics.html            # Аналитика на основе ORM aggregate() и annotate()
│       └── includes/
│           ├── event_card.html        # Карточка события с иконкой и ответственным
│           └── event_status.html      # Бейдж статуса события
│
├── categories/                        # Django-приложение: Категории событий (ПР9 ORM)
│   ├── models.py                      # Модель Category (name, description, icon)
│   ├── views.py                       # categories (список с annotate), category_detail (404)
│   ├── urls.py                        # namespace 'categories'
│   ├── migrations/
│   │   └── 0001_initial.py            # Начальная миграция модели Category
│   └── templates/categories/
│       ├── category_list.html         # Список категорий со счётчиком связанных событий
│       ├── category_detail.html       # Детальная страница категории и её события
│       └── includes/
│           └── category_card.html     # Карточка категории
│
├── users/                             # Django-приложение: Пользователи (ПР9 ORM)
│   ├── models.py                      # Модель User (name, email)
│   ├── views.py                       # Представления пользователей
│   ├── urls.py                        # Маршруты пользователей
│   └── migrations/
│       └── 0001_initial.py            # Начальная миграция модели User
│
├── templates/                         # Общепроектные шаблоны
│   ├── base.html                      # Базовый каркас сайта с навигацией и футером
│   ├── 404.html                       # Страница ошибки 404
│   └── includes/
│       └── navigation.html            # Навигационное меню сайта
│
├── tests/                             # Автоматизированные тесты pytest (40 тестов)
│   ├── test_calendar.py               # Тесты логики событий (ПР1–ПР3)
│   ├── test_categories.py             # Тесты моделей категорий
│   ├── test_database.py               # Тесты схемы, связей, импорта и SQL-запросов (ПР7)
│   ├── test_main.py                   # Тесты консольного меню
│   ├── test_users.py                  # Тесты пользователей
│   ├── test_views.py                  # Тесты Django view-функций и страниц через ORM
│   └── test_orm.py                    # Комплексные тесты моделей, связей, Q, фильтров, Paginator (ПР9)
│
└── reports/                           # Отчёты по практическим работам
    ├── create_reports.py              # Генератор отчётов docx (ПР1, ПР2, ПР3, ПР5, ПР6, ПР7, ПР9)
    └── tasks/                         # Исходные методические указания (PDF)
```

---

## 6. Пользовательские сценарии и маршруты веб-приложения

1. **Главная страница (`/`)** — `homepage:index`:
   - Отображает сводку метрик через Django ORM: общее количество событий (`count()`), количество выполненных дел (`filter(is_completed=True)`), предстоящих дел (`filter(is_completed=False)`), общее число категорий, а также три ближайших события через `select_related('category', 'user')[:3]`.
2. **Список всех событий с фильтрацией и пагинацией (`/events/`)** — `events:list`:
   - Выводит события с возможностью фильтрации по категории (`category_id`), ответственному пользователю (`user_id`), дате (`event_date`) и статусу (`status=active/completed`).
   - Поддерживает сортировку по дате (`date_asc`, `date_desc`), названию (`name_asc`), категории (`category`) и пользователю (`user`).
   - Постраничный вывод по 5 событий на страницу (`Paginator`) с сохранением всех GET-параметров фильтрации и сортировки в ссылках пагинации через `{% querystring %}`.
3. **Многокритериальный поиск событий (`/events/search/`)** — `events:search`:
   - Форма поиска по тексту и дате; выполняет поиск через `Q`-объекты по названию события, названию категории и имени ответственного пользователя (`Q(name__icontains=q) | Q(category__name__icontains=q) | Q(user__name__icontains=q)`).
4. **Статистика семейного календаря (`/events/statistics/`)** — `events:statistics`:
   - Аналитика на основе ORM-агрегатов: `Event.objects.aggregate(Count, Min, Max)`, распределение событий по категориям через `Category.objects.annotate(events_count=Count('events'))`, распределение по пользователям `User.objects.annotate(events_count=Count('events'))`, популярные категории (`events_count > 1`).
5. **Карточка события (`/events/<id>/`)** — `events:detail`:
   - Загружает событие через `get_object_or_404(Event, id=event_id)` с отображением связанных объектов (`event.category`, `event.user`), email ответственного, оставшихся дней и статуса.
6. **Список категорий (`/categories/`)** — `categories:list`:
   - Карточки категорий с подсчётом привязанных событий через `annotate(events_count=Count('events'))`.
7. **Детальная страница категории (`/categories/<id>/`)** — `categories:detail`:
   - Карточка категории с описанием и списком всех привязанных событий через обратную связь `category.events.all()`. При обращении к несуществующему идентификатору возвращается страница 404.

---

## 7. Запуск и проверка проекта

### Запуск веб-сервера Django:
```bash
python manage.py runserver
```
Веб-интерфейс доступен в браузере по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Управление миграциями базы данных:
```bash
# Создание миграций при изменении моделей:
python manage.py makemigrations

# Применение миграций:
python manage.py migrate

# Проверка статуса применённых миграций:
python manage.py showmigrations
```

### Перенос данных из SQLite ПР7 в Django ORM:
```bash
python db/import_sqlite_to_orm.py
```

### Проверка конфигурации Django:
```bash
python manage.py check
```
Команда завершается сообщением `System check identified no issues (0 silenced)`.

### Запуск интерактивной консоли Django Shell:
```bash
python manage.py shell
```

### Запуск автоматических тестов (pytest):
```bash
pytest -v
```
Все **40 тестов** (логика консольного сценария, модели, целостность SQLite ПР7, Django ORM модели, связи, QuerySet, Q-поиск, срезы, Paginator, маршруты и представления) выполняются успешно (100% pass).

### Проверка стиля кода (flake8):
```bash
flake8 . --extend-exclude=venv
```
Код на 100% соответствует стандарту PEP 8 (0 предупреждений и ошибок).

### Генерация отчётов:
```bash
python reports/create_reports.py
```
Формирует актуальные docx-отчёты в каталоге `reports/`, включая `Отчет_ПР9_Соленов.docx`.
