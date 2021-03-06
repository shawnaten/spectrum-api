# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 23:46
from __future__ import unicode_literals

import cal.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0003_remove_person_banner_id'),
        ('cal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='roster.Person')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='checkin_code',
            field=models.CharField(default=cal.models.gen_checkin_code, max_length=4),
        ),
        migrations.AddField(
            model_name='checkin',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cal.Event'),
        ),
    ]
