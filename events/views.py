from django.shortcuts import render
from models.events import find_event_by_id
from storage import load_all_events


def events(request):
    events_list = load_all_events("data/events.json")
    context = {
        "events": events_list,
    }
    return render(
        request,
        "events/event_list.html",
        context,
    )


def event_detail(request, event_id):
    events_list = load_all_events("data/events.json")
    event = find_event_by_id(events_list, event_id)

    days_left = event.days_until() if event else None

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
