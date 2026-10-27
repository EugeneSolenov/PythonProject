from django.shortcuts import render
from db.database import get_connection


def index(request):
    """Главная страница: сводка метрик и ближайшие события из SQLite."""
    conn = get_connection()
    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_events,
            SUM(CASE WHEN is_completed = 0 THEN 1 ELSE 0 END)
                AS upcoming_count,
            SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END)
                AS completed_count
        FROM events;
    """).fetchone()

    cat_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM categories;"
    ).fetchone()["cnt"]

    recent_events = conn.execute("""
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
        ORDER BY events.event_date ASC
        LIMIT 3;
    """).fetchall()
    conn.close()

    total_events = summary["total_events"] if summary else 0
    upcoming_count = (
        summary["upcoming_count"]
        if summary and summary["upcoming_count"]
        else 0
    )
    completed_count = (
        summary["completed_count"]
        if summary and summary["completed_count"]
        else 0
    )

    context = {
        "total_events": total_events,
        "upcoming_count": upcoming_count,
        "completed_count": completed_count,
        "categories_count": cat_count,
        "recent_events": recent_events,
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception=None):
    """Кастомный обработчик ошибки 404."""
    return render(request, "404.html", status=404)
