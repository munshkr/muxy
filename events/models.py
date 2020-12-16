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
    preparation_time = models.PositiveIntegerField(default=5)
    rtmp_url = RTMPURLField(blank=True, null=True)
    public_rtmp_url = RTMPURLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

    def is_active_at(self, at):
        return self.active and self.starts_at <= at and at < self.ends_at

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError("Event ends before starting")

        if self.duration:
            duration_in_minutes = self.duration.total_seconds() // 60
            if self.preparation_time > duration_in_minutes:
                raise ValidationError(
                    "Preparation time (%d) is longer than the duration of the event (%d)"
                    % (self.preparation_time, duration_in_minutes))

    @property
    def resolved_rtmp_url(self):
        if self.rtmp_url:
            return resolve_url(self.rtmp_url)

    @property
    def duration(self):
        if self.starts_at and self.ends_at:
            return self.ends_at - self.starts_at


def get_uuid4():
    return str(uuid.uuid4())


class Stream(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    publisher_name = models.CharField(max_length=200, blank=True)
    publisher_email = models.EmailField(blank=True)
    description = models.CharField(max_length=255, blank=True)
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
    def active_range(self):
        return (self.starts_at, self.ends_at)

    @property
    def preparing_range(self):
        begin, _ = self.active_range
        return (begin - timedelta(minutes=self.event.preparation_time), begin)

    @property
    def valid_range(self):
        begin, _ = self.preparing_range
        _, end = self.active_range
        return (begin, end)

    def is_active_at(self, at):
        """Whether stream is active and is allowed to stream to the event server"""
        begin, end = self.active_range
        return self.event.is_active_at(at) and begin <= at and at < end

    def is_preparing_at(self, at):
        """Whether stream is at the preparation phase

        Stream is allowed to stream to Muxy but not to the event server

        """
        begin, end = self.preparing_range
        return begin <= at and at < end

    def is_valid_at(self, at):
        """Whether stream is preparing or active; i.e. is allowed to stream to Muxy"""
        return self.is_preparing_at(at) or self.is_active_at(at)

    def clean(self):
        if self.pk and self.starts_at and self.ends_at:
            other_streams = Stream.objects.filter(
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at).exclude(pk=self.pk)
            if other_streams.exists():
                raise ValidationError("There are other simultaneous streams")

    # FIXME: Should be a property of Event
    @property
    def resolved_rtmp_url(self):
        if self.event.rtmp_url:
            # FIXME: Use a slug for publisher name
            return self.event.resolved_rtmp_url.format(slug=self.slug)
