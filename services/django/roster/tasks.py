from celery import shared_task
import logging

from roster.models import Person


@shared_task
def import_csv(file):
    with open(file) as f:
        content = f.readlines()

        for line in content:
            tokens = line.split(",")
            if len(tokens) != 3:
                break
            first = tokens[0].strip()
            last = tokens[1].strip()
            phone = "+1" + tokens[2].strip()

            try:
                person = Person.objects.get(phone=phone)
                person.first = first
                person.last = last
                person.save()
            except Exception as err:
                logging.warn("Failed to import {0} {1}.".format(first, last))
