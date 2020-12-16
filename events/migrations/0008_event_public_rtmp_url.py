# Generated by Django 3.1.4 on 2020-12-16 03:18

from django.db import migrations
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_event_contact_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='public_rtmp_url',
            field=events.models.RTMPURLField(blank=True, null=True),
        ),
    ]
