# Generated by Django 3.1.4 on 2020-12-07 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20201207_0032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='rtmp_url',
        ),
        migrations.CreateModel(
            name='StreamingService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('CS', 'Custom'), ('YT', 'Youtube'), ('TW', 'Twitch')], default='YT', max_length=2)),
                ('server', models.CharField(max_length=200)),
                ('key', models.CharField(max_length=200)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]