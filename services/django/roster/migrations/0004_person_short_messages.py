# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-03 03:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0003_remove_person_banner_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='short_messages',
            field=models.BooleanField(default=False),
        ),
    ]