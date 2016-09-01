from celery import shared_task
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery
from apiclient.errors import HttpError
from datetime import datetime, time, timezone

import strict_rfc3339 as rfc3339

from cal.models import Calendar, Event, RSVPSettings


@shared_task
def sync(name, cal_id):
    http_auth = get_http_auth()
    cal_api = discovery.build('calendar', 'v3', http=http_auth)

    calendar = None
    keep_syncing = True

    while keep_syncing:
        calendar, created = Calendar.objects.get_or_create(
            cal_id=cal_id,
            defaults={"name": name}
        )

        if not calendar.sync_token and not calendar.page_token:
            print("case 1")
            request = cal_api.events().list(
                calendarId=cal_id,
                timeMin=rfc3339.now_to_rfc3339_utcoffset(),
                timeZone="UTC"
            )
        elif not calendar.page_token:
            print("case 2")
            request = cal_api.events().list(
                calendarId=cal_id,
                timeZone="UTC",
                syncToken=calendar.sync_token
            )
        else:
            print("case 3")
            request = cal_api.events().list(
                calendarId=cal_id,
                timeZone="UTC",
                syncToken=calendar.sync_token,
                pageToken=calendar.page_token
            )
        try:
            events_result = request.execute()
            events = events_result.get('items', [])
            process_events(calendar, events)
            if "nextPageToken" in events_result:
                calendar.page_token = events_result.get("nextPageToken")
            if "nextSyncToken" in events_result:
                calendar.sync_token = events_result.get("nextSyncToken")
            if not calendar.page_token:
                keep_syncing = False
        except HttpError as err:
            if err.resp.status == 410:
                calendar.delete()
            else:
                print("Error syncing calendar: " + name + " " + str(err))
                keep_syncing = False

        calendar.save()


def process_events(calendar, events):
    for event in events:
        event_id = event.get("id")
        values = {}

        values["status"] = event.get("status")

        if values["status"] == Event.CANCELLED:
            model = Event.objects.get(
                calendar_id=calendar.id,
                event_id=event_id
            )
            model.delete()
            continue

        if "summary" in event:
            values["summary"] = event.get("summary")
        if "description" in event:
            values["description"] = event.get("description")
        if "location" in event:
            values["location"] = event.get("location")

        if event.get("recurrence"):
            values["recurring"] = True
        else:
            values["recurring"] = False

        values["start"] = set_datetime(event.get("start"))
        values["end"] = set_datetime(event.get("end"))

        db_event, created = Event.objects.update_or_create(
            calendar_id=calendar.id,
            event_id=event_id,
            defaults=values
        )

        rsvp_settings, created = RSVPSettings.objects.get_or_create(
            event=db_event
        )


def set_datetime(data):
    if "date" in data.keys():
        value = data["date"]
        value = datetime.strptime(value + "+0000", "%Y-%m-%d%z")
    else:
        value = data["dateTime"]
        value = rfc3339.rfc3339_to_timestamp(value)
        value = datetime.fromtimestamp(value, timezone.utc)

    return value


def get_http_auth():
    scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "./google_keyfile.json", scopes)
    return credentials.authorize(Http())
