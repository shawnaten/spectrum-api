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


def finish(session, context, key, val=None):
    context[key] = val if val is not None else True
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

    intent = value(entities, session, "intent")
    rsvp_intent = value(entities, session, "rsvp_intent")
    event_summary = value(entities, session, "event_summary")

    if not event_summary:
        return finish(session, context, "not_found")

    start = datetime_value(entities, session)
    if start:
        end = start + timedelta(days=1)
        if end < datetime.now(timezone.utc):
            return finish(session, context, "not_found")

    try:
        if start:
            event = Event.objects.get(
                summary__icontains=event_summary,
                start__range=[start, end]
            )
        else:
            event = Event.objects.get(summary__icontains=event_summary)
    except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
        return finish(session, context, "not_found")

    event_settings = event.settings
    rsvp_enabled = event_settings.rsvp_enabled
    rsvp_limit = event_settings.rsvp_limit
    rsvp_message = event_settings.rsvp_message
    rsvp_count = RSVP.objects.filter(event=event).count()
    rsvp_exists = RSVP.objects.filter(event=event, person=person).exists()

    if rsvp_intent == "count":

        if not rsvp_enabled:
            return finish(session, context, "disabled")
        elif rsvp_count == 0:
            return finish(session, context, "none")
        elif rsvp_count == 1:
            return finish(session, context, "single")
        else:
            return finish(session, context, "count", rsvp_count)

    elif rsvp_intent == "rsvp" and not rsvp_exists:

        if not rsvp_enabled:
            return finish(session, context, "disabled")
        elif event.start <= datetime.now(timezone.utc):
            return finish(session, context, "full")
        elif rsvp_limit is not None and rsvp_count >= rsvp_limit:
            return finish(session, context, "full")
        else:
            RSVP(event=event, person=person).save()
            context["summary"] = event.summary
            start = event.start.astimezone(timezone(-timedelta(hours=5)))
            context["time"] = datetime.strftime(start, "%a, %b %d, %I:%M %p")
            send_sms.delay(person.id, rsvp_message)
            return finish(session, context, "location", event.location)

    elif rsvp_intent == "rsvp" and rsvp_exists:
        return finish(session, context, "rsvp_dup")
    elif rsvp_intent == "unrsvp" and rsvp_exists:
        RSVP.objects.filter(event=event, person=person).delete()
        return finish(session, context, "unrsvpd")
    else:
        return finish(session, context, "unrsvp_dup")


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
        return finish(session, context, "not_found")

    checkin_enabled = event_settings.checkin_enabled
    event = event_settings.event

    if not checkin_enabled:
        return finish(session, context, "not_found")

    now = datetime.now(timezone.utc)
    cutoff = event.start + (event.end - event.start) / 2
    if now < event.start:
        return finish(session, context, "early")
    elif now > cutoff:
        checkin_exists = Checkin.objects.filter(
            person=person,
            event=event_settings.event
        ).exists()
        if checkin_exists:
            return finish(session, context, "duplicate")
        else:
            return finish(session, context, "late")

    checkin_obj, is_new_checkin = Checkin.objects.get_or_create(
        person=person,
        event=event_settings.event
    )

    if not is_new_checkin:
        return finish(session, context, "duplicate")

    return finish(session, context, "success")

actions = {
    'send': send,
    'rsvp': rsvp,
    'first_name': first_name,
    'checkin': checkin,
}
