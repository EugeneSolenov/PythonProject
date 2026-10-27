from datetime import date, datetime
from django.shortcuts import render
from db.database import get_connection


def events(request):
    """Отображение списка всех событий из SQLite с данными о категориях."""
    conn = get_connection()
    events_list = conn.execute("""
        SELECT
            events.id,
            events.name,
            events.event_date,
            events.is_completed,
            events.user_id,
            events.category_id,
            categories.name AS category,
            categories.icon AS category_icon,
            users.name AS user_name
        FROM events
        JOIN categories ON events.category_id = categories.id
        JOIN users ON events.user_id = users.id
        ORDER BY events.event_date ASC;
    """).fetchall()
    conn.close()
    return render(
        request,
        "events/event_list.html",
        {"events": events_list},
    )


def event_detail(request, event_id):
    """Детальная карточка события по идентификатору."""
    conn = get_connection()
    event = conn.execute("""
        SELECT
            events.id,
            events.name,
            events.event_date,
            events.is_completed,
            events.user_id,
            events.category_id,
            categories.name AS category,
            categories.icon AS category_icon,
            users.name AS user_name,
            users.email AS user_email
        FROM events
        JOIN categories ON events.category_id = categories.id
        JOIN users ON events.user_id = users.id
        WHERE events.id = ?;
    """, [event_id]).fetchone()
    conn.close()

    days_left = None
    if event is not None:
        try:
            ev_date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()
            days_left = (ev_date - date.today()).days
        except (ValueError, TypeError):
            days_left = None

    context = {
        "event": event,
        "days_left": days_left,
    }
    return render(
        request,
        "events/event_detail.html",
        context,
        status=404 if event is None else 200,
    )


def search_events(request):
    """Поиск событий на выбранную дату (параметризованный SQL-запрос)."""
    search_date = request.GET.get("date", "").strip()
    events_found = []
    if search_date:
        conn = get_connection()
        events_found = conn.execute("""
            SELECT
                events.id,
                events.name,
                events.event_date,
                events.is_completed,
                categories.name AS category,
                categories.icon AS category_icon,
                users.name AS user_name
            FROM events
            JOIN categories ON events.category_id = categories.id
            JOIN users ON events.user_id = users.id
            WHERE events.event_date = ?
            ORDER BY events.name ASC;
        """, [search_date]).fetchall()
        conn.close()

    return render(
        request,
        "events/search.html",
        {
            "search_date": search_date,
            "events": events_found,
        },
    )


def statistics(request):
    """Статистика календаря на основе SQL-агрегатов и группировок."""
    conn = get_connection()

    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_events,
            SUM(CASE WHEN is_completed = 0 THEN 1 ELSE 0 END)
                AS active_events,
            SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END)
                AS completed_events,
            MIN(event_date) AS earliest_date,
            MAX(event_date) AS latest_date
        FROM events;
    """).fetchone()

    category_stats = conn.execute("""
        SELECT
            categories.id AS category_id,
            categories.name AS category_name,
            categories.icon AS category_icon,
            COUNT(events.id) AS events_count
        FROM categories
        LEFT JOIN events ON categories.id = events.category_id
        GROUP BY categories.id, categories.name, categories.icon
        ORDER BY events_count DESC, categories.name ASC;
    """).fetchall()

    user_stats = conn.execute("""
        SELECT
            users.id AS user_id,
            users.name AS user_name,
            users.email AS user_email,
            COUNT(events.id) AS events_count
        FROM users
        LEFT JOIN events ON users.id = events.user_id
        GROUP BY users.id, users.name, users.email
        ORDER BY events_count DESC;
    """).fetchall()

    popular_categories = conn.execute("""
        SELECT
            categories.name AS category_name,
            COUNT(events.id) AS events_count
        FROM categories
        JOIN events ON categories.id = events.category_id
        GROUP BY categories.id, categories.name
        HAVING COUNT(events.id) > 1
        ORDER BY events_count DESC;
    """).fetchall()

    conn.close()

    context = {
        "summary": summary,
        "category_stats": category_stats,
        "user_stats": user_stats,
        "popular_categories": popular_categories,
    }
    return render(request, "events/statistics.html", context)
