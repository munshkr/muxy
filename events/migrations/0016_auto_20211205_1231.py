# Generated by Django 3.1.4 on 2021-12-05 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_customapikey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventstreamurl',
            name='url',
            field=models.URLField(),
        ),
        migrations.AlterUniqueTogether(
            name='eventstreamurl',
            unique_together={('event', 'url')},
        ),
    ]
