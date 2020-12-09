import uuid

from django.core import validators
from django.core.exceptions import ValidationError
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
    rtmp_url = RTMPURLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def is_active_at(self, at):
        return self.active and self.starts_at <= at and at < self.ends_at

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError("Event ends before starting")


class Stream(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    publisher_name = models.CharField(max_length=200, blank=True)
    publisher_email = models.EmailField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    stream_key = models.UUIDField(default=uuid.uuid4, editable=False)
    live_at = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        return '{event_name}: {publisher_name} ({starts_at} - {ends_at})'.format(
            event_name=self.event.name,
            publisher_name=self.publisher_name,
            starts_at=self.starts_at,
            ends_at=self.ends_at)

    def is_active_at(self, at):
        return self.event.is_active_at(
            at) and self.starts_at <= at and at < self.ends_at

    def clean(self):
        if self.pk and self.starts_at and self.ends_at:
            other_streams = Stream.objects.filter(
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at).exclude(pk=self.pk)
            if other_streams.exists():
                raise ValidationError("There are other simultaneous streams")