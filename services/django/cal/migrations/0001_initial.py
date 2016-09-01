# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-28 08:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('cal_id', models.CharField(max_length=200)),
                ('page_token', models.CharField(blank=True, max_length=200)),
                ('sync_token', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=200)),
                ('summary', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('confirmed', 'confirmed'), ('tentative', 'tentative'), ('cancelled', 'cancelled')], max_length=10)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('recurring', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='RSVP',
            fields=[
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='roster.Person')),
            ],
            options={
                'verbose_name_plural': "RSVP's",
                'verbose_name': 'RSVP',
            },
        ),
        migrations.CreateModel(
            name='RSVPSettings',
            fields=[
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='cal.Event')),
                ('enabled', models.BooleanField(default=False)),
                ('limit', models.IntegerField(blank=True, null=True)),
                ('message', models.CharField(blank=True, max_length=160)),
            ],
            options={
                'verbose_name_plural': 'RSVP settings',
                'verbose_name': 'RSVP setting',
            },
        ),
        migrations.AddField(
            model_name='rsvp',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cal.Event'),
        ),
        migrations.AddField(
            model_name='event',
            name='calendar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cal.Calendar'),
        ),
    ]