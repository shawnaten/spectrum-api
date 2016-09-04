import os
import logging
import traceback

from celery import shared_task
from wit import Wit

from roster.models import Person
from chatbot.models import Session, Message, SessionData
from chatbot.tasks import send_sms
from chatbot.wit_actions import actions


wit = Wit(access_token=os.environ["WIT_ACCESS_TOKEN"], actions=actions)


@shared_task
def process_sms(phone, text):
    person, is_new_person = Person.objects.get_or_create(phone=phone)
    session, is_new_session = Session.objects.get_or_create(
        person=person
    )

    if is_new_person:
        sys_message, created = Message.objects.get_or_create(tag="welcome")
        send_sms.delay(person.id, sys_message.text)

    try:
        context = {}
        context = wit.run_actions(session.conv_id, text, context)
        session.refresh_from_db()
        if session.finished:
            session.reset_conv_id()
    except Exception as err:
        logging.error(traceback.format_exc())
        sys_message, created = Message.objects.get_or_create(
            tag="wit_actions_error")
        send_sms.delay(person.id, sys_message.text)
        session.delete()
