# Generated by Django 3.1.4 on 2021-11-30 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20201219_1915'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventStreamURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_urls', to='events.event')),
            ],
        ),
    ]
