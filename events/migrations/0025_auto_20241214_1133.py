# Generated by Django 3.1.14 on 2024-12-14 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_stream_description'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stream',
            unique_together={('event', 'starts_at'), ('event', 'ends_at')},
        ),
    ]