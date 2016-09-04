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
from chatbot.wit_util import value, datetime_value, finish, check_intent
from backend.util import log_debug


def send(request, response):
    session = Session.objects.get(conv_id=request["session_id"])
    send_sms.delay(session.person.id, response["text"])


def rsvp(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    log_debug(person)
    check_intent(entities, session)

    rsvp_type = value(entities, session, "rsvp_type")
    event_summary = value(entities, session, "event")

    if not event_summary:
        return finish(session, context, "not_found", False)

    start = datetime_value(entities, session)
    if start:
        end = start + timedelta(days=1)
        if end < datetime.now(timezone.utc):
            return finish(session, context, "not_found", False)

    try:
        if start:
            event = Event.objects.get(
                summary__icontains=event_summary,
                start__range=[start, end]
            )
        else:
            event = Event.objects.get(
                summary__icontains=event_summary
                start__gte=datetime.now(timezone.utc)
            )
    except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
        return finish(session, context, "not_found", False)

    event_settings = event.settings
    rsvp_enabled = event_settings.rsvp_enabled
    rsvp_limit = event_settings.rsvp_limit
    rsvp_message = event_settings.rsvp_message
    rsvp_count = RSVP.objects.filter(event=event).count()
    rsvp_exists = RSVP.objects.filter(event=event, person=person).exists()

    if rsvp_type == "count":

        if not rsvp_enabled:
            return finish(session, context, "disabled")
        elif rsvp_count == 0:
            return finish(session, context, "none")
        elif rsvp_count == 1:
            return finish(session, context, "single")
        else:
            return finish(session, context, "count", val=rsvp_count)

    elif rsvp_type == "rsvp" and not rsvp_exists:

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
            return finish(session, context, "location", val=event.location)

    elif rsvp_type == "rsvp" and rsvp_exists:
        return finish(session, context, "rsvp_dup")
    elif rsvp_type == "unrsvp" and rsvp_exists:
        RSVP.objects.filter(event=event, person=person).delete()
        return finish(session, context, "unrsvpd")
    else:
        return finish(session, context, "unrsvp_dup")


def first_name(request):
    context = request["context"]
    text = request["text"]
    session = Session.objects.get(conv_id=request["session_id"])
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
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

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
