# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 04:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0013_auto_20160904_0417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkin',
            name='event',
        ),
        migrations.RemoveField(
            model_name='checkin',
            name='person',
        ),
        migrations.RemoveField(
            model_name='rsvp',
            name='event',
        ),
        migrations.RemoveField(
            model_name='rsvp',
            name='person',
        ),
        migrations.DeleteModel(
            name='Checkin',
        ),
        migrations.DeleteModel(
            name='RSVP',
        ),
    ]
