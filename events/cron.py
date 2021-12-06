import os
from datetime import timedelta
from string import Template

from django.apps import apps
from django.core.mail import EmailMessage
from django.db.models import Q
from django.utils import timezone
from django_cron import CronJobBase, Schedule

from .models import Stream, StreamNotification
from .utils import get_formatted_stream_timeframe


class NotifyStreamPreparingJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "muxy.events.cron.notify_stream_preparing"
    template_path = os.path.join(
        apps.get_app_config("events").path,
        "templates",
        "emails",
        "stream_preparing.txt",
    )
    subject = '$event_name: Your stream "$name" is about to start!'

    def do(self):
        now = timezone.now()
        streams_in_preparing = Stream.objects.filter(
            Q(starts_at__lte=now + timedelta(minutes=10)) & Q(starts_at__gt=now)
        ).all()

        for stream in streams_in_preparing:
            preparing_notif = stream.streamnotification_set.filter(
                Q(kind=StreamNotification.Kinds.PREPARING)
            ).first()

            if not preparing_notif:
                self.send_email(stream)

    def send_email(self, stream):
        now = timezone.now()

        with open(self.template_path) as f:
            body_tpl = f.read()

        starts_in = (stream.starts_at - now).seconds // 60
        starts_at, ends_at = get_formatted_stream_timeframe(stream)
        variables = dict(
            name=stream.publisher_name,
            event_name=stream.event.name,
            starts_at=starts_at,
            ends_at=ends_at,
            rtmp_url=stream.event.public_rtmp_url,
            key=stream.key,
            contact_email=stream.event.contact_email,
            starts_in=starts_in,
            preparation_time=stream.event.preparation_time,
        )

        body = Template(body_tpl).safe_substitute(variables)
        subject = Template(self.subject).safe_substitute(variables)
        to = [stream.publisher_email]
        headers = {"Reply-To": stream.event.contact_email}
        msg = EmailMessage(subject, body, None, to, headers=headers)

        msg.send(fail_silently=False)

        StreamNotification.objects.create(
            stream=stream, kind=StreamNotification.Kinds.PREPARING, sent_at=now
        )
