import os
import logging

from datetime import datetime, timezone
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from roster.models import Person
from chatbot.models import Message
from cal.models import EventSettings, Checkin
from chatbot.sms_tasks import send_sms

INTENT_CHECKIN = "checkin"

KEYWORDS = [
    INTENT_CHECKIN,
]


@shared_task
def process_message(phone, message):
    person, is_new_person = Person.objects.get_or_create(phone=phone)
    welcome_msg, _ = Message.objects.get_or_create(tag="welcome")
    unsure_msg, _ = Message.objects.get_or_create(tag="unsure")
    invalid_msg, _ = Message.objects.get_or_create(tag="invalid")
    apple = "good"

    apppple += "and green"
    if is_new_person:
        send_sms.delay(person.id, welcome_msg.id)

    intent = determine_intent(message)

    if intent == INTENT_CHECKIN:

        tokens = message.split()
        if len(tokens) != 2 or len(tokens[1]) != 4:
            send_sms.delay(person.id, invalid_msg.id)
        else:
            checkin(person, tokens[1].lower())

    else:
        send_sms.delay(person.id, unsure_msg.id)


def determine_intent(message):
    message = message.lower()

    for keyword in KEYWORDS:
        if keyword in message:
            return keyword
    return None


def checkin(person, short_code):
    not_found_msg, _ = Message.objects.get_or_create(tag="checkin_not_found")
    early_msg, _ = Message.objects.get_or_create(tag="checkin_early")
    late_msg, _ = Message.objects.get_or_create(tag="checkin_late")
    duplicate_msg, _ = Message.objects.get_or_create(tag="checkin_duplicate")
    success_msg, _ = Message.objects.get_or_create(tag="checkin_success")

    try:
        event_settings = EventSettings.objects.get(short_code=short_code)
    except ObjectDoesNotExist as err:
        return send_sms.delay(person.id, not_found_msg.id)

    checkin_enabled = event_settings.checkin_enabled
    checkin_message = event_settings.checkin_message
    event = event_settings.event

    if not checkin_enabled:
        return send_sms.delay(person.id, not_found_msg.id)

    now = datetime.now(timezone.utc)
    cutoff = event.start + (event.end - event.start) / 2
    if now < event.start:
        return send_sms.delay(person.id, early_msg.id)
    elif now > cutoff:
        checkin_exists = Checkin.objects.filter(
            person=person,
            event=event_settings.event
        ).exists()
        if checkin_exists:
            return send_sms.delay(person.id, duplicate_msg.id)
        else:
            return send_sms.delay(person.id, late_msg.id)

    checkin_obj, is_new_checkin = Checkin.objects.get_or_create(
        person=person,
        event=event_settings.event
    )

    if not is_new_checkin:
        return send_sms.delay(person.id, duplicate_msg.id)

    if checkin_message:
        send_sms.delay(person.id, checkin_message.id)
    return send_sms.delay(person.id, success_msg.id)
