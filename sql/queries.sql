-- ==========================================
-- Семейный календарь: проверенные SQL-запросы (ПР7)
-- ==========================================

-- 1. Выборка списков: Получение всех событий календаря, отсортированных по дате
SELECT
    id,
    name,
    event_date,
    is_completed
FROM events
ORDER BY event_date ASC;

-- 2. Выборка списков: Получение полного списка категорий событий с сортировкой по названию
SELECT
    id,
    name,
    description,
    icon
FROM categories
ORDER BY name ASC;

-- 3. Фильтрация WHERE: Выборка только актуальных (невыполненных) событий
SELECT
    id,
    name,
    event_date,
    category_id
FROM events
WHERE is_completed = 0
ORDER BY event_date ASC;

-- 4. Фильтрация WHERE: Поиск событий на выбранную дату (для поисковой формы)
SELECT
    id,
    name,
    event_date,
    user_id,
    category_id
FROM events
WHERE event_date = '2026-10-20'
ORDER BY name;

-- 5. Соединение таблиц JOIN: Полная информация о событиях со сведениями о категории и пользователе
SELECT
    events.id,
    events.name AS event_name,
    events.event_date,
    events.is_completed,
    categories.name AS category_name,
    categories.icon AS category_icon,
    users.name AS user_name,
    users.email AS user_email
FROM events
JOIN categories ON events.category_id = categories.id
JOIN users ON events.user_id = users.id
ORDER BY events.event_date ASC;

-- 6. Соединение таблиц JOIN: Получение активных событий конкретного члена семьи
SELECT
    events.id,
    events.name AS event_name,
    events.event_date,
    categories.name AS category_name,
    users.name AS user_name
FROM events
JOIN categories ON events.category_id = categories.id
JOIN users ON events.user_id = users.id
WHERE events.is_completed = 0
  AND users.id = 1
ORDER BY events.event_date ASC;

-- 7. Агрегирующие функции: Сводная статистика по статусам событий и крайним датам
SELECT
    COUNT(*) AS total_events,
    SUM(CASE WHEN is_completed = 0 THEN 1 ELSE 0 END) AS active_events,
    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) AS completed_events,
    MIN(event_date) AS earliest_event_date,
    MAX(event_date) AS latest_event_date
FROM events;

-- 8. Агрегирующие функции: Подсчёт пользователей и категорий в системе
SELECT
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM categories) AS total_categories;

-- 9. Группировка GROUP BY + LEFT JOIN: Распределение событий по категориям (включая пустые категории)
SELECT
    categories.id AS category_id,
    categories.name AS category_name,
    categories.icon AS category_icon,
    COUNT(events.id) AS events_count
FROM categories
LEFT JOIN events ON categories.id = events.category_id
GROUP BY categories.id, categories.name, categories.icon
ORDER BY events_count DESC, categories.name ASC;

-- 10. Группировка GROUP BY + LEFT JOIN: Распределение событий по членам семьи
SELECT
    users.id AS user_id,
    users.name AS user_name,
    COUNT(events.id) AS events_count
FROM users
LEFT JOIN events ON users.id = events.user_id
GROUP BY users.id, users.name
ORDER BY events_count DESC;

-- 11. Фильтрация групп HAVING: Популярные категории, содержащие более одного события
SELECT
    categories.name AS category_name,
    COUNT(events.id) AS events_count
FROM categories
JOIN events ON categories.id = events.category_id
GROUP BY categories.id, categories.name
HAVING COUNT(events.id) > 1
ORDER BY events_count DESC;

-- 12. Подзапрос NOT IN: Поиск членов семьи, свободных от событий на указанную дату
SELECT
    users.id,
    users.name,
    users.email
FROM users
WHERE users.id NOT IN (
    SELECT events.user_id
    FROM events
    WHERE events.event_date = '2026-10-20'
      AND events.is_completed = 0
)
ORDER BY users.name;
