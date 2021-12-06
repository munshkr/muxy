# Generated by Django 3.1.4 on 2021-12-06 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20211206_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSupportURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('name', models.CharField(blank=True, max_length=255)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_urls', to='events.event')),
            ],
            options={
                'unique_together': {('event', 'url')},
            },
        ),
    ]
