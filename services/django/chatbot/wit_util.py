from datetime import datetime, timezone

import strict_rfc3339 as rfc3339
from django.core.exceptions import ObjectDoesNotExist

from chatbot.models import SessionData


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


def finish(session, context, key, reset_conv=True, val=None):
    context[key] = val if val is not None else True
    if reset_conv:
        session.reset_conv_id()
    else:
        session.save()
    return context


def check_intent(entities, session):
    changed = False
    new_intent = first_entity_value(entities, "intent")
    try:
        session_data = SessionData.objects.get(session=session, key="intent")
        if new_val != session_data.val:
            changed = True
    except ObjectDoesNotExist as err:
        changed = False

    if changed:
        SessionData.objects.filter(session=session).delete()

    SessionData.objects.update_or_create(
        session=session,
        key="intent",
        defaults={"val": new_intent}
    )
