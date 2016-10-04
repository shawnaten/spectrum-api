# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-28 02:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0008_auto_20160928_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 9, 28, 2, 32, 6, 960856)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
