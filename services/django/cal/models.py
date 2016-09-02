import uuid

from django.db import models

from roster.models import Person


def gen_checkin_code():
    id = uuid.uuid4()
    return id.hex[:4]


class Calendar(models.Model):
    name = models.CharField(max_length=100)
    cal_id = models.CharField(max_length=200)
    page_token = models.CharField(max_length=200, blank=True)
    sync_token = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (CONFIRMED, 'confirmed'),
        (TENTATIVE, 'tentative'),
        (CANCELLED, 'cancelled'),
    )

    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    event_id = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    start = models.DateTimeField()
    end = models.DateTimeField()
    recurring = models.BooleanField()

    def __str__(self):
        return self.summary


class EventSettings(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True
    )
    short_code = models.CharField(max_length=4, default=gen_checkin_code)
    rsvp_enabled = models.BooleanField(default=False)
    rsvp_limit = models.IntegerField(null=True, blank=True)
    rsvp_message = models.CharField(blank=True, max_length=160)
    checkin_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Event setting'
        verbose_name_plural = 'Event settings'

    def __str__(self):
        return str(self.event)


class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True
    )

    class Meta:
        verbose_name = 'RSVP'
        verbose_name_plural = 'RSVP\'s'

    def __str__(self):
        return "{0} @ {1}".format(self.person, self.event)


class Checkin(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True
    )
