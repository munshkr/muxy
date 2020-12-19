# Generated by Django 3.1.4 on 2020-12-19 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_event_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('CR', 'Created'), ('PR', 'Preparing')], max_length=2)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.stream')),
            ],
        ),
    ]
