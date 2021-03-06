# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-02 07:05
from __future__ import unicode_literals

import cal.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0002_auto_20160831_2346'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckinSettings',
            fields=[
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='cal.Event')),
                ('enabled', models.BooleanField(default=False)),
                ('short_code', models.CharField(default=cal.models.gen_checkin_code, max_length=4)),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='checkin_code',
        ),
    ]
