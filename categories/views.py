from django.shortcuts import render
from db.database import get_connection


def categories(request):
    """Список категорий событий с подсчётом числа событий (GROUP BY)."""
    conn = get_connection()
    categories_list = conn.execute("""
        SELECT
            categories.id,
            categories.name,
            categories.description,
            categories.icon,
            COUNT(events.id) AS events_count
        FROM categories
        LEFT JOIN events ON categories.id = events.category_id
        GROUP BY
            categories.id,
            categories.name,
            categories.description,
            categories.icon
        ORDER BY categories.name ASC;
    """).fetchall()
    conn.close()

    context = {
        "categories": categories_list,
    }
    return render(
        request,
        "categories/category_list.html",
        context,
    )


def category_detail(request, category_id):
    """Детальная информация о категории и список привязанных к ней событий."""
    conn = get_connection()
    category = conn.execute("""
        SELECT id, name, description, icon
        FROM categories
        WHERE id = ?;
    """, [category_id]).fetchone()

    category_events = []
    if category is not None:
        category_events = conn.execute("""
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
            WHERE events.category_id = ?
            ORDER BY events.event_date ASC;
        """, [category_id]).fetchall()
    conn.close()

    context = {
        "category": category,
        "events": category_events,
    }

    return render(
        request,
        "categories/category_detail.html",
        context,
        status=404 if category is None else 200,
    )
