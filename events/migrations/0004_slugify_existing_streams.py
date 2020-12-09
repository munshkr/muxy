# Generated by Django 3.1.4 on 2020-12-09 16:12

from django.db import migrations


def slugify_streams(apps, schema_editor):
    Stream = apps.get_model('events', 'Stream')
    for stream in Stream.objects.all():
        # Trigger slug update
        stream.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_stream_slug'),
    ]

    operations = [
        migrations.RunPython(slugify_streams, migrations.RunPython.noop)
    ]
