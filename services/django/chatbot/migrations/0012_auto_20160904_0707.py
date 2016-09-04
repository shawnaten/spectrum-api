# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 07:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_auto_20160904_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 9, 4, 7, 7, 48, 821216, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sessiondata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 9, 4, 7, 7, 54, 653501, tzinfo=utc)),
            preserve_default=False,
        ),
    ]