from datetime import date
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q
from django.shortcuts import render

from categories.models import Category
from events.models import Event
from users.models import User


def events(request):
    """Список событий через ORM с фильтрацией, сортировкой и пагинацией."""
    events_qs = Event.objects.select_related("category", "user")

    # 1. Чтение параметров фильтрации
    date_str = request.GET.get("date", "").strip()
    category_id = request.GET.get("category", "").strip()
    user_id = request.GET.get("user", "").strip()
    status_filter = request.GET.get("status", "").strip()
    error = None

    # Фильтрация по дате
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
            events_qs = events_qs.filter(event_date=selected_date)
        except ValueError:
            error = "Некорректный формат даты (ожидается ГГГГ-ММ-ДД)"

    # Фильтрация по категории (связанная модель)
    if category_id.isdigit():
        events_qs = events_qs.filter(category_id=int(category_id))

    # Фильтрация по пользователю (связанная модель)
    if user_id.isdigit():
        events_qs = events_qs.filter(user_id=int(user_id))

    # Исключение записей с помощью exclude() или фильтрация по статусу
    if status_filter == "active":
        events_qs = events_qs.exclude(is_completed=True)
    elif status_filter == "completed":
        events_qs = events_qs.filter(is_completed=True)

    # 2. Сортировка
    sort = request.GET.get("sort", "date").strip()
    sort_fields = {
        "date": ["event_date", "pk"],
        "-date": ["-event_date", "-pk"],
        "name": ["name", "event_date"],
        "category": ["category__name", "event_date"],
        "user": ["user__name", "event_date"],
    }
    ordering = sort_fields.get(sort, ["event_date", "pk"])
    events_qs = events_qs.order_by(*ordering)

    # 3. Пагинация (по 5 событий на страницу)
    total_count = events_qs.count()
    paginator = Paginator(events_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "events": page_obj,
        "page_obj": page_obj,
        "total_count": total_count,
        "selected_date": date_str,
        "selected_category": category_id,
        "selected_user": user_id,
        "selected_status": status_filter,
        "sort": sort,
        "categories": Category.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(
        request,
        "events/event_list.html",
        context,
    )


def event_detail(request, event_id):
    """Детальная карточка события по идентификатору через Django ORM."""
    event = (
        Event.objects
        .select_related("category", "user")
        .filter(pk=event_id)
        .first()
    )

    days_left = event.days_until() if event is not None else None

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
    """Поиск событий по дате и/или строковому запросу через Django ORM."""
    search_date = request.GET.get("date", "").strip()
    query = request.GET.get("q", "").strip()
    events_found = []

    if search_date or query:
        events_qs = Event.objects.select_related("category", "user")

        if search_date:
            try:
                parsed_date = date.fromisoformat(search_date)
                events_qs = events_qs.filter(event_date=parsed_date)
            except ValueError:
                pass

        if query:
            events_qs = events_qs.filter(
                Q(name__icontains=query)
                | Q(category__name__icontains=query)
                | Q(user__name__icontains=query)
            )

        events_found = events_qs.order_by("event_date", "name")

    return render(
        request,
        "events/search.html",
        {
            "search_date": search_date,
            "query": query,
            "events": events_found,
        },
    )


def statistics(request):
    """Статистика календаря на основе Django ORM (aggregate, annotate)."""
    # Сводные показатели через aggregate
    summary = Event.objects.aggregate(
        total_events=Count("id"),
        active_events=Count("id", filter=Q(is_completed=False)),
        completed_events=Count("id", filter=Q(is_completed=True)),
        earliest_date=Min("event_date"),
        latest_date=Max("event_date"),
    )

    # Распределение по категориям (LEFT JOIN + GROUP BY)
    category_stats = (
        Category.objects
        .annotate(
            category_name=F("name"),
            category_icon=F("icon"),
            events_count=Count("events"),
        )
        .values("id", "category_name", "category_icon", "events_count")
        .order_by("-events_count", "category_name")
    )

    # Распределение по пользователям (LEFT JOIN + GROUP BY)
    user_stats = (
        User.objects
        .annotate(
            user_name=F("name"),
            user_email=F("email"),
            events_count=Count("events"),
        )
        .values("id", "user_name", "user_email", "events_count")
        .order_by("-events_count", "user_name")
    )

    # Популярные категории с количеством событий > 1 (GROUP BY + HAVING)
    popular_categories = (
        Category.objects
        .annotate(
            category_name=F("name"),
            events_count=Count("events"),
        )
        .filter(events_count__gt=1)
        .values("category_name", "events_count")
        .order_by("-events_count")
    )

    context = {
        "summary": summary,
        "category_stats": category_stats,
        "user_stats": user_stats,
        "popular_categories": popular_categories,
    }
    return render(request, "events/statistics.html", context)
