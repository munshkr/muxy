import os
from string import Template

from django.apps import apps
from django.core.mail import EmailMessage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Stream, StreamNotification
from .utils import get_formatted_stream_timeframe


@receiver(post_save, sender=Stream)
def send_stream_create_or_update_email(sender, instance, created, **kwargs):
    if created:
        send_stream_create_email(instance)
    # else:
    #    send_stream_update_email(instance)


@receiver(post_delete, sender=Stream)
def send_stream_destroy_email(sender, instance, **kwargs):
    subject = "$event_name: You have removed your stream $name"
    variables = dict(
        name=instance.publisher_name,
        event_name=instance.event.name,
    )
    send_stream_email(
        instance,
        template_name="stream_destroy",
        variables=variables,
        subject=subject,
        kind=StreamNotification.Kinds.REMOVED,
    )


def send_stream_create_email(stream):
    subject = "$event_name: Thank you for signing up!"
    starts_at, ends_at = get_formatted_stream_timeframe(stream)
    variables = dict(
        name=stream.publisher_name,
        event_name=stream.event.name,
        starts_at=starts_at,
        ends_at=ends_at,
        rtmp_url=stream.event.public_rtmp_url,
        key=stream.key,
        preparation_time=stream.event.preparation_time,
    )
    send_stream_email(
        stream,
        template_name="stream_create",
        variables=variables,
        subject=subject,
        kind=StreamNotification.Kinds.CREATED,
    )


def send_stream_update_email(stream):
    subject = "$event_name: You have updated your stream $name"
    variables = dict(
        name=stream.publisher_name,
        event_name=stream.event.name,
        description=stream.description,
        location=stream.location,
    )
    send_stream_email(
        stream,
        template_name="stream_update",
        variables=variables,
        subject=subject,
        kind=StreamNotification.Kinds.UPDATED,
    )


def send_stream_email(stream, *, template_name, variables, subject, kind):
    template_path = os.path.join(
        apps.get_app_config("events").path,
        "templates",
        "emails",
        f"{template_name}.txt",
    )
    with open(template_path) as f:
        body_tpl = f.read()

    body = Template(body_tpl).safe_substitute(variables)
    subject = Template(subject).safe_substitute(variables)
    to = [stream.publisher_email]
    headers = {"Reply-To": stream.event.contact_email}
    msg = EmailMessage(subject, body, None, to, headers=headers)

    msg.send(fail_silently=False)

    stream = None if kind == StreamNotification.Kinds.REMOVED else stream
    StreamNotification.objects.create(stream=stream, kind=kind, sent_at=timezone.now())
