import os
import logging

from celery import shared_task
from twilio.rest import TwilioRestClient

from roster.models import Person
from chatbot.models import Message

twilio = TwilioRestClient()


@shared_task
def send_sms_raw(person_id, message):
    person = Person.objects.get(pk=person_id)

    twilio.messages.create(
        to=person.phone,
        from_=os.environ["TWILIO_NUMBER"],
        body=message
    )


@shared_task
def send_sms(person_id, message_tag):
    person = Person.objects.get(pk=person_id)
    message, _ = Message.objects.get_or_create(tag=message_tag)

    twilio.messages.create(
        to=person.phone,
        from_=os.environ["TWILIO_NUMBER"],
        body=message.body
    )
