import os
from string import Template

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from events.models import Event, Stream


class Command(BaseCommand):
    help = 'Sends a notification email to publishers from an event'

    def add_arguments(self, parser):
        parser.add_argument('-T',
                            '--template',
                            required=True,
                            help='path to a custom body template .txt file')
        parser.add_argument('-E',
                            '--event',
                            required=True,
                            type=int,
                            help='event id')
        parser.add_argument('--subject', required=True, help='email subject')
        parser.add_argument(
            '--streams',
            nargs='+',
            type=int,
            help='only send notification to publishers from specific stream ids'
        )

    def handle(self, *args, **options):
        event_id = options['event']

        if 'only' in options and options['only']:
            ids = [int(id_s) for id_s in options['only']]
            streams = Stream.objects.filter(event=event_id, pk=ids).all()
            if not streams.exists():
                raise CommandError('Streams with ids %s do not exist.' % ids)
        else:
            event = Event.objects.filter(pk=event_id).first()
            if not event:
                raise CommandError('Event id %d does not exist.' % event_id)
            streams = Stream.objects.filter(event=event).all()
            if not streams.exists():
                raise CommandError('Event id %d has no streams.' % event_id)

        if not event.contact_email:
            raise CommandError('Event has no contact email.')

        template_path = options['template']
        if not os.path.exists(template_path):
            raise CommandError('Template file %s does not exist.' %
                               template_path)

        with open(template_path) as f:
            body_tpl = f.read()

        for stream in streams:
            variables = dict(name=stream.publisher_name,
                             event_name=stream.event.name,
                             starts_at=stream.starts_at.strftime('%c %Z'),
                             ends_at=stream.ends_at.strftime('%c %Z'),
                             rtmp_url=stream.event.public_rtmp_url,
                             key=stream.key,
                             contact_email=stream.event.contact_email,
                             preparation_time=stream.event.preparation_time)

            body = Template(body_tpl).safe_substitute(variables)
            subject = Template(options['subject']).safe_substitute(variables)

            to = [stream.publisher_email]
            self.stdout.write('Send email to %s with subject "%s"' %
                              (to, subject))
            send_mail(
                subject,
                body,
                event.contact_email,
                to,
                fail_silently=False,
            )

        self.stdout.write(self.style.SUCCESS('Successfully sent emails'))
