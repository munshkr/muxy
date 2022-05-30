# Generated by Django 3.1.13 on 2022-05-30 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_eventsupporturl'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamArchiveURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('name', models.CharField(blank=True, max_length=255)),
                ('stream', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.stream')),
            ],
            options={
                'unique_together': {('stream', 'url')},
            },
        ),
    ]