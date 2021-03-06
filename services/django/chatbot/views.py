from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

from twilio.twiml import Response
from twilio.util import RequestValidator

import logging
import os

# from chatbot.wit_tasks import process_sms
from chatbot.process_tasks import process_message

validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])


def sms(request):
    # Validate that request came from Twilio service.
    uri = request.build_absolute_uri()
    signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")

    if not validator.validate(uri, {}, signature):
        logging.warn("Request did not come from Twilio.")
        return HttpResponseNotFound()

    # Process message using simple keywords
    process_message.delay(request.GET)

    # Send empty response because we send messages seperately
    return HttpResponse(Response())
