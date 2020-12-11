import socket
import uuid
from urllib.parse import urlparse
from datetime import timedelta

from autoslug import AutoSlugField
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.fields import URLField as FormURLField
from django.utils import timezone


def resolve_url(url):
    parsed = urlparse(url)
    ip = socket.gethostbyname(parsed.hostname)
    n = ''
    if parsed.username:
        n += parsed.username
        if parsed.password:
            n += ':{}'.format(parsed.password)
        n += '@'
    n += str(ip)
    if parsed.port:
        n += ':{}'.format(parsed.port)
    return parsed._replace(netloc=n).geturl()


class RTMPURLFormField(FormURLField):
    default_validators = [validators.URLValidator(schemes=['rtmp'])]


class RTMPURLField(models.URLField):
    '''URL field that accepts URLs that start with rtmp:// only.'''
    default_validators = [validators.URLValidator(schemes=['rtmp'])]

    def formfield(self, **kwargs):
        return super(RTMPURLField,
                     self).formfield(**{
                         'form_class': RTMPURLFormField,
                     })


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    rtmp_url = RTMPURLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def is_active_at(self, at):
        return self.active and self.starts_at <= at and at < self.ends_at

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError("Event ends before starting")

    @property
    def resolved_rtmp_url(self):
        if self.rtmp_url:
            return resolve_url(self.rtmp_url)


def get_uuid4():
    return str(uuid.uuid4())


class Stream(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    publisher_name = models.CharField(max_length=200, blank=True)
    publisher_email = models.EmailField(blank=True)
    slug = AutoSlugField(null=True,
                         default=None,
                         populate_from='publisher_name',
                         unique_with=['publisher_name', 'starts_at'])
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    key = models.CharField(max_length=36,
                           default=get_uuid4,
                           editable=True,
                           unique=True)
    live_at = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        return '{event_name}: {publisher_name} ({starts_at} - {ends_at})'.format(
            event_name=self.event.name,
            publisher_name=self.publisher_name,
            starts_at=self.starts_at,
            ends_at=self.ends_at)

    @property
    def valid_range(self):
        starts_at = self.starts_at - timedelta(minutes=5)
        ends_at = self.ends_at
        return (starts_at, ends_at)

    def is_active_at(self, at):
        starts_at, ends_at = self.valid_range
        return self.event.is_active_at(at) and starts_at <= at and at < ends_at

    def clean(self):
        if self.pk and self.starts_at and self.ends_at:
            other_streams = Stream.objects.filter(
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at).exclude(pk=self.pk)
            if other_streams.exists():
                raise ValidationError("There are other simultaneous streams")

    @property
    def resolved_rtmp_url(self):
        if self.event.rtmp_url:
            # FIXME: Use a slug for publisher name
            return self.event.resolved_rtmp_url.format(slug=self.slug)
