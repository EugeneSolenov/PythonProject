from django.shortcuts import render

from categories.models import Category
from events.models import Event


def index(request):
    """Главная страница: сводка метрик и ближайшие события через Django ORM."""
    total_events = Event.objects.count()
    upcoming_count = Event.objects.filter(is_completed=False).count()
    completed_count = Event.objects.filter(is_completed=True).count()
    categories_count = Category.objects.count()

    recent_events = (
        Event.objects
        .select_related("category", "user")
        .order_by("event_date")[:3]
    )

    context = {
        "total_events": total_events,
        "upcoming_count": upcoming_count,
        "completed_count": completed_count,
        "categories_count": categories_count,
        "recent_events": recent_events,
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception=None):
    """Кастомный обработчик ошибки 404."""
    return render(request, "404.html", status=404)
