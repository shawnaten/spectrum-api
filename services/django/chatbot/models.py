import uuid

from django.db import models

from roster.models import Person


def gen_id():
    id = uuid.uuid4()
    return id.hex


class Message(models.Model):
    tag = models.CharField(max_length=100)
    text = models.CharField(
        max_length=160,
        default="🤖 Whoops this message is empty."
    )

    def __str__(self):
        return self.tag


class Session(models.Model):
    conv_id = models.CharField(
        max_length=36,
        default=gen_id,
    )
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE
    )
    finished = models.BooleanField(default=False)

    def reset_conv_id(self):
        self.conv_id = gen_id()
        self.save()

    def __str__(self):
        person = self.person
        if person.first and person.last:
            return person.first + " " + person.last
        else:
            return person.phone


class SessionData(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    val = models.TextField(blank=True)

    def __str__(self):
        return self.key
