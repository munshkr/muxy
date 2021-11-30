import os
from string import Template

from django.apps import apps
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Stream, StreamNotification


@receiver(post_save, sender=Stream)
def send_stream_create_email(sender, instance, created, **kwargs):
    stream = instance
    template_path = os.path.join(
        apps.get_app_config("events").path, "templates", "emails", "stream_create.txt"
    )
    subject = "$event_name: Thank you for signing up!"

    if created:
        now = timezone.now()

        with open(template_path) as f:
            body_tpl = f.read()

        variables = dict(
            name=stream.publisher_name,
            event_name=stream.event.name,
            starts_at=stream.starts_at.strftime("%c %Z"),
            ends_at=stream.ends_at.strftime("%c %Z"),
            rtmp_url=stream.event.public_rtmp_url,
            key=stream.key,
            preparation_time=stream.event.preparation_time,
        )

        body = Template(body_tpl).safe_substitute(variables)
        subject = Template(subject).safe_substitute(variables)
        to = [stream.publisher_email]
        headers = {"Reply-To": stream.event.contact_email}
        msg = EmailMessage(subject, body, None, to, headers=headers)

        msg.send(fail_silently=False)

        StreamNotification.objects.create(
            stream=stream, kind=StreamNotification.Kinds.CREATED, sent_at=now
        )
