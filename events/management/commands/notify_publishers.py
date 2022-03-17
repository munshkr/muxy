import os
from string import Template

from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from events.models import Event, Stream
from events.utils import get_formatted_stream_timeframe


class Command(BaseCommand):
    help = "Sends a notification email to publishers from an event"

    def add_arguments(self, parser):
        parser.add_argument(
            "-T",
            "--template",
            required=True,
            help="path to a custom body template .txt file",
        )
        parser.add_argument("-E", "--event", required=True, type=int, help="event id")
        parser.add_argument("--subject", required=True, help="email subject")
        parser.add_argument(
            "--streams",
            nargs="+",
            type=int,
            help="only send notification to publishers from specific stream ids",
        )

    def handle(self, *args, **options):
        event_id = options["event"]
        event = Event.objects.filter(pk=event_id).first()
        if not event:
            raise CommandError("Event id %d does not exist." % event_id)

        if "streams" in options and options["streams"]:
            streams = Stream.objects.filter(
                event=event, pk__in=options["streams"]
            ).all()
            if not streams.exists():
                raise CommandError("Streams with ids %s do not exist." % ids)
        else:
            streams = Stream.objects.filter(event=event).all()
            if not streams.exists():
                raise CommandError("Event id %d has no streams." % event_id)

        if not event.contact_email:
            raise CommandError("Event has no contact email.")

        template_path = options["template"]
        if not os.path.exists(template_path):
            raise CommandError("Template file %s does not exist." % template_path)

        with open(template_path) as f:
            body_tpl = f.read()

        for stream in streams:
            starts_at, ends_at = get_formatted_stream_timeframe(stream)
            variables = dict(
                name=stream.publisher_name,
                event_name=stream.event.name,
                starts_at=starts_at,
                ends_at=ends_at,
                rtmp_url=stream.event.public_rtmp_url,
                key=stream.key,
                contact_email=stream.event.contact_email,
                preparation_time=stream.event.preparation_time,
            )

            body = Template(body_tpl).safe_substitute(variables)
            subject = Template(options["subject"]).safe_substitute(variables)
            to = [stream.publisher_email]
            headers = {"Reply-To": stream.event.contact_email}
            msg = EmailMessage(subject, body, None, to, headers=headers)

            self.stdout.write('Send email to %s with subject "%s"' % (to, subject))
            msg.send(fail_silently=False)

        self.stdout.write(self.style.SUCCESS("Successfully sent emails"))
