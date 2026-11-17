from django.db.models import Count
from django.shortcuts import render

from categories.models import Category


def categories(request):
    """Список категорий событий с подсчётом числа событий через ORM."""
    categories_list = (
        Category.objects
        .annotate(events_count=Count("events"))
        .order_by("name")
    )
    context = {
        "categories": categories_list,
    }
    return render(
        request,
        "categories/category_list.html",
        context,
    )


def category_detail(request, category_id):
    """Детальная информация о категории и список её событий через ORM."""
    category = Category.objects.filter(pk=category_id).first()

    category_events = []
    if category is not None:
        category_events = (
            category.events
            .select_related("user", "category")
            .order_by("event_date")
        )

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
