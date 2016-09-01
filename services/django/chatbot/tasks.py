import os
import logging

from celery import shared_task
from twilio.rest import TwilioRestClient

from roster.models import Person

twilio = TwilioRestClient()


@shared_task
def send_sms(person_id, message):
    person = Person.objects.get(pk=person_id)

    twilio.messages.create(
        to=person.phone,
        from_=os.environ["TWILIO_NUMBER"],
        body=message
    )
