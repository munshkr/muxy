import uuid

from django.core import validators
from django.db import models
from django.forms.fields import URLField as FormURLField
from django.utils import timezone


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

    def __str__(self):
        return '{name} ({starts_at} - {ends_at})'.format(
            name=self.name, starts_at=self.starts_at, ends_at=self.ends_at)

    def is_valid_at(self, at):
        return self.active and self.starts_at <= at and at < self.ends_at


class Stream(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    publisher_name = models.CharField(max_length=200, blank=True)
    publisher_email = models.EmailField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    stream_key = models.UUIDField(default=uuid.uuid4, editable=False)
    live_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{event_name}: {publisher_name} ({starts_at} - {ends_at})'.format(
            event_name=self.event.name,
            publisher_name=self.publisher_name,
            starts_at=self.starts_at,
            ends_at=self.ends_at)

    def is_valid_at(self, at):
        return self.event.is_valid_at(
            at) and self.starts_at <= at and at < self.ends_at
