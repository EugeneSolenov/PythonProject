from django.shortcuts import render
from storage import load_all_events, load_categories


def index(request):
    events = load_all_events("data/events.json")
    categories = load_categories("data/categories.json")

    # Сводные данные для главной страницы
    upcoming_events = [e for e in events if e.is_upcoming()]
    completed_events = [e for e in events if e.is_completed]

    context = {
        "total_events": len(events),
        "upcoming_count": len(upcoming_events),
        "completed_count": len(completed_events),
        "categories_count": len(categories),
        "recent_events": events[:3],
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)
