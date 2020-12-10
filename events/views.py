import json

from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from rest_framework import permissions, viewsets

from events.models import Event, Stream
from events.serializers import EventSerializer, StreamSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all().order_by('-starts_at')


class StreamViewSet(viewsets.ModelViewSet):
    serializer_class = StreamSerializer
    queryset = Stream.objects.all().order_by('-starts_at')


@require_POST
def on_publish(request):
    # nginx-rtmp makes the stream name available in the POST body via `name`
    stream_key = request.POST['name']

    # Lookup the activity and verify the publisher is allowed to stream.
    stream = get_object_or_404(Stream, key=stream_key)

    now = timezone.now()

    # Check if stream is valid
    if not stream.is_active_at(now, allow_preparation=True):
        print("[PUBLISH] Stream is not active at %s" % (now))
        return HttpResponseForbidden("Stream is not active now")

    # Set the stream live
    stream.live_at = now
    stream.save()

    event = stream.event
    # If event has a custom RTMP URL, redirect to it
    if event.rtmp_url:
        return HttpResponseRedirect(stream.resolved_rtmp_url)
    else:
        return HttpResponse("OK")


@require_POST
def on_publish_done(request):
    # When a stream stops nginx-rtmp will still dispatch callbacks
    # using the original stream key, not the redirected stream name.
    stream_key = request.POST['name']

    # Set the stream offline
    Stream.objects.filter(key=stream_key).update(live_at=None)

    # Response is ignored.
    return HttpResponse("OK")


@require_POST
def on_update(request):
    stream_key = request.POST['name']
    stream = get_object_or_404(Stream, key=stream_key)

    now = timezone.now()
    if not stream.is_active_at(now):
        print("[UPDATE] Stream is not valid at %s" % (now))
        return HttpResponseForbidden("Stream is not active now")

    return HttpResponse("OK")
