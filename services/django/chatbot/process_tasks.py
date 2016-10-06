import os
import logging

from datetime import datetime, timezone, timedelta
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from roster.models import Person
from chatbot.models import Message
from cal.models import Event, EventSettings, Checkin
from chatbot.sms_tasks import send_sms, send_sms_raw

INTENT_CHECKIN = "checkin"
INTENT_MORE_INFO = "more info"
INTENT_ATTEN_SUMMARY = "attendance summary"

KEYWORDS = [
    INTENT_CHECKIN,
    INTENT_MORE_INFO,
    INTENT_ATTEN_SUMMARY
]


@shared_task
def process_message(params):
    phone = params.get("From", "")
    message = params.get("Body", "")

    person, is_new_person = Person.objects.get_or_create(phone=phone)

    if is_new_person:
        send_sms.delay(person.id, "welcome")

    intent = determine_intent(message)

    if intent == INTENT_CHECKIN:

        tokens = message.split()
        if len(tokens) != 2 or len(tokens[1]) != 4:
            send_sms.delay(person.id, "invalid")
        else:
            checkin(person, tokens[1].lower())

    elif intent == INTENT_MORE_INFO:
        more_info(person)

    elif intent == INTENT_ATTEN_SUMMARY:
        send_sms_raw.delay(person.id, get_attendance_summary())

    else:
        send_sms.delay(person.id, "unsure")


def determine_intent(message):
    message = message.lower()

    for keyword in KEYWORDS:
        if keyword in message:
            return keyword
    return None


def checkin(person, short_code):

    try:
        event_settings = EventSettings.objects.get(short_code=short_code)
    except ObjectDoesNotExist as err:
        return send_sms.delay(person.id, "checkin_not_found")

    checkin_enabled = event_settings.checkin_enabled
    checkin_message = event_settings.checkin_message
    event = event_settings.event

    if not checkin_enabled:
        return send_sms.delay(person.id, "checkin_not_found")

    now = datetime.now(timezone.utc)
    cutoff = event.start + (event.end - event.start) / 2
    if now < event.start:
        return send_sms.delay(person.id, "checkin_early")
    elif now > cutoff:
        checkin_exists = Checkin.objects.filter(
            person=person,
            event=event_settings.event
        ).exists()
        if checkin_exists:
            return send_sms.delay(person.id, "checkin_duplicate")
        else:
            return send_sms.delay(person.id, "checkin_late")

    checkin_obj, is_new_checkin = Checkin.objects.get_or_create(
        person=person,
        event=event_settings.event
    )

    if not is_new_checkin:
        return send_sms.delay(person.id, "checkin_duplicate")

    if checkin_message:
        send_sms.delay(person.id, checkin_message.tag)
    return send_sms.delay(person.id, "checkin_success")


def more_info(person):
    upcoming_events = get_upcoming_events()
    send_sms.delay(person.id, "more_info")
    send_sms_raw.delay(person.id, upcoming_events)


def get_upcoming_events():
    message, _ = Message.objects.get_or_create(tag="upcoming_events_base")
    message = message.body
    start = datetime.now(timezone.utc)
    end = start + timedelta(weeks=1)
    events = Event.objects.filter(
        start__range=[start, end]
    )

    day = -1
    message += "\n"
    for event in events:
        start = event.start.astimezone(timezone(-timedelta(hours=5)))
        end = event.end.astimezone(timezone(-timedelta(hours=5)))

        if end - start == timedelta(hours=24):
            continue

        if start.day != day:
            day = start.day
            message += "\n" + datetime.strftime(start, "%A") + "\n"

        when = datetime.strftime(start, "%I:%M %p")
        message += "- {0} @ {1}\n".format(event.summary, when)

    message = message.strip()
    return message


def get_attendance_summary():
    event_settings = []
    events = []
    checkins = {}
    message = ""

    event_settings = EventSettings.objects.filter(checkin_enabled=True)[:10]
    for settings in event_settings:
        events.append(settings.event)
    for event in events:
        checkins[event] = Checkins.objects.filter(event=event)

    if len(events) == 0:
        return "☹️ No attendance has been recorded at any event."

    for event in events:
        message += "{summary}: {count}\n".format(
            summary=event.summary,
            checkins=len(checkins[event])
        )

    return message
