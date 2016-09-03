import os
import logging
from datetime import datetime, timezone, timedelta

import strict_rfc3339 as rfc3339
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DataError

from roster.models import Person
from chatbot.models import Session, Message, SessionData
from cal.models import Event, RSVP, Checkin, EventSettings
from chatbot.tasks import send_sms


def first_entity_value(entities, entity):
    if entity not in entities.keys():
        return ""
    val = entities[entity][0]["value"]
    if not val:
        return ""
    return val["value"] if isinstance(val, dict) else val


def value(entities, session, key):
    val = first_entity_value(entities, key)
    session_data, created = SessionData.objects.get_or_create(
        session=session,
        key=key,
        defaults={"val": val}
    )
    if val and not created:
        session_data.val = val
        session_data.save()

    return session_data.val


def datetime_value(entities, session):
    string = value(entities, session, "datetime")
    if not string:
        return None
    timestamp = rfc3339.rfc3339_to_timestamp(string)
    return datetime.fromtimestamp(timestamp, timezone.utc)


def finish(session, context, key, finished):
    context[key] = True
    session.finished = finished
    session.save()
    return context


def send(request, response):
    session = Session.objects.get(id=request["session_id"])
    send_sms.delay(session.person.id, response["text"])


def rsvp(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(id=request["session_id"])
    person = session.person

    rsvp_intent = value(entities, session, "rsvp_intent")
    event_type = value(entities, session, "event")

    if not event_type:
        context["not_found"] = True
        session.save()
        return context

    start = datetime_value(entities, session)
    if start:
        end = start + timedelta(days=1)
        if end < datetime.now(timezone.utc):
            context["not_found"] = True
            session.save()
            return context

    try:
        if start:
            event = Event.objects.get(
                summary__icontains=event_type,
                start__range=[start, end]
            )
        else:
            event = Event.objects.get(summary__icontains=event_type)
    except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
        context["not_found"] = True
        session.save()
        return context

    event_settings = event.settings
    rsvp_enabled = event_settings.rsvp_enabled
    rsvp_limit = event_settings.rsvp_limit
    rsvp_message = event_settings.rsvp_message
    rsvp_count = RSVP.objects.filter(event=event).count()
    rsvp_exists = RSVP.objects.filter(event=event, person=person).exists()

    if rsvp_intent == "count":

        if not rsvp_enabled:
            context["disabled"] = True
        elif rsvp_count == 0:
            context["none"] = True
        elif rsvp_count == 1:
            context["single"] = True
        else:
            context["count"] = rsvp_count

    elif rsvp_intent == "rsvp" and not rsvp_exists:

        if not rsvp_enabled:
            context["disabled"] = True
        elif event.start <= datetime.now(timezone.utc):
            context["full"] = True
        elif rsvp_limit is not None and rsvp_count >= rsvp_limit:
            context["full"] = True
        else:
            RSVP(event=event, person=person).save()
            context["summary"] = event.summary
            start = event.start.astimezone(timezone(-timedelta(hours=5)))
            context["time"] = datetime.strftime(start, "%a, %b %d, %I:%M %p")
            context["location"] = event.location
            send_sms.delay(person.id, rsvp_message)

    elif rsvp_intent == "rsvp" and rsvp_exists:
        context["rsvp_dup"] = True
    elif rsvp_intent == "unrsvp" and rsvp_exists:
        RSVP.objects.filter(event=event, person=person).delete()
        context["unrsvpd"] = True
    else:
        context["unrsvp_dup"] = True

    session.finished = True
    session.save()
    return context


def first_name(request):
    context = request["context"]
    text = request["text"]
    session = Session.objects.get(id=request["session_id"])
    person = session.person

    try:
        person.first = text
        person.save()
        context["success"] = True
    except DataError as err:
        context["failure"] = True

    return context


def checkin(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(id=request["session_id"])
    person = session.person
    short_code = value(entities, session, "short_code")

    try:
        event_settings = EventSettings.objects.get(short_code=short_code)
    except ObjectDoesNotExist as err:
        return finish(session, context, "not_found", True)

    checkin_enabled = event_settings.checkin_enabled
    event = event_settings.event

    if not checkin_enabled:
        return finish(session, context, "not_found", True)

    now = datetime.now(timezone.utc)
    cutoff = event.start + (event.end - event.start) / 2
    if now < event.start:
        return finish(session, context, "early", True)
    elif now > cutoff:
        return finish(session, context, "late", True)

    checkin_obj, is_new_checkin = Checkin.objects.get_or_create(
        person=person,
        event=event_settings.event
    )

    if not is_new_checkin:
        return finish(session, context, "duplicate", True)

    return finish(session, context, "success", True)

actions = {
    'send': send,
    'rsvp': rsvp,
    'first_name': first_name,
    'checkin': checkin,
}
