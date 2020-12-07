import uuid

from django.core import validators
from django.db import models
from django.forms.fields import URLField as FormURLField


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


class Participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    url = models.URLField(blank=True)

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    participants = models.ManyToManyField(Participant, through='EventSlot')
    rtmp_url = models.CharField(blank=True, max_length=254)

    def __str__(self):
        return f'{self.name} ({self.starts_at} - {self.ends_at})'


class EventSlot(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    stream_key = models.UUIDField(default=uuid.uuid4, editable=False)
    live_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.event.name}: {self.participant} ({self.starts_at} - {self.ends_at})'
