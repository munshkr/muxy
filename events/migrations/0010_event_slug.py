# Generated by Django 3.1.4 on 2020-12-16 22:16

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_stream_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='name', unique='name'),
        ),
    ]
