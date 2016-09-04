import os
import logging
from datetime import datetime, timezone, timedelta

import strict_rfc3339 as rfc3339
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DataError

from roster.models import Person
from chatbot.models import Session, Message, SessionData
from cal.models import Event, RSVP, Checkin, EventSettings
from chatbot.tasks import send_sms, send_sms_raw
from chatbot.wit_util import value, datetime_value, finish, check_intent
from backend.util import log_debug


def send(request, response):
    session = Session.objects.get(conv_id=request["session_id"])
    send_sms_raw.delay(session.person.id, response["text"])


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
                summary__icontains=event_summary,
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
            if rsvp_message:
                send_sms.delay(person.id, rsvp_message.id)
            return finish(session, context, "location", val=event.location)

    elif rsvp_type == "rsvp" and rsvp_exists:
        return finish(session, context, "rsvp_dup")
    elif rsvp_type == "unrsvp" and rsvp_exists:
        RSVP.objects.filter(event=event, person=person).delete()
        return finish(session, context, "unrsvpd")
    else:
        return finish(session, context, "unrsvp_dup")


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
    checkin_message = event_settings.checkin_message
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

    if checkin_message:
        send_sms.delay(person.id, checkin_message.id)
    return finish(session, context, "success")


def name(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

    text = request["text"]
    text = text.title()
    tokens = text.split()

    if len(tokens) < 2:
        return finish(session, context, "failure", False)

    person.first = tokens[0]
    person.last = ""
    for token in tokens[1:]:
        person.last += token + " "
    person.last = person.last.strip()

    try:
        person.save()
    except DataError as err:
        return finish(session, context, "failure", False)

    return finish(session, context, "success", False)


def email(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

    email = value(entities, session, "email")

    if not email:
        return finish(session, context, "failure", False)

    person.email = email
    try:
        person.save()
    except DataError as err:
        return finish(session, context, "failure", False)

    return finish(session, context, "success", False)


def classification(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

    classification = value(entities, session, "classification")

    if not classification:
        return finish(session, context, "failure", False)

    person.classification = classification
    try:
        person.save()
    except DataError as err:
        return finish(session, context, "failure", False)

    return finish(session, context, "success", False)


def photo_consent(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

    yes_no = value(entities, session, "yes_no")

    if yes_no == "yes":
        person.photo_consent = True
        person.save()
        return finish(session, context, "granted")
    else:
        person.photo_consent = False
        person.save()
        return finish(session, context, "denied")


def check_profile(request):
    context = request["context"]
    entities = request["entities"]
    session = Session.objects.get(conv_id=request["session_id"])
    person = session.person

    check_intent(entities, session)

    form_str = "Name: {name}\nEmail: {email}\nClassification: {year}\n"
    form_str += "Photos: {photos}"
    year = person.classification if person.classification else "None"
    year = year.title()
    info = form_str.format(
        name=person.first + " " + person.last if person.first else "None",
        email=person.email if person.email else "None",
        year=year,
        photos="Accepted" if person.photo_consent else "Declined",
    )

    return finish(session, context, "info", val=info)


actions = {
    "send": send,
    "rsvp": rsvp,
    "name": name,
    "checkin": checkin,
    "email": email,
    "classification": classification,
    "photo_consent": photo_consent,
    "check_profile": check_profile,
}
