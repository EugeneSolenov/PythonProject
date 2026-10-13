from django.shortcuts import render
from models.categories import find_category_by_id
from storage import load_all_events, load_categories


def categories(request):
    categories_list = load_categories("data/categories.json")
    events_list = load_all_events("data/events.json")

    # Подсчитаем события по категориям
    counts = {}
    for cat in categories_list:
        counts[cat.name] = len([
            e for e in events_list
            if e.category.casefold() == cat.name.casefold()
        ])

    context = {
        "categories": categories_list,
        "counts": counts,
    }
    return render(
        request,
        "categories/category_list.html",
        context,
    )


def category_detail(request, category_id):
    categories_list = load_categories("data/categories.json")
    category = find_category_by_id(categories_list, category_id)

    category_events = []
    if category is not None:
        events_list = load_all_events("data/events.json")
        category_events = [
            e for e in events_list
            if e.category.casefold() == category.name.casefold()
        ]

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
