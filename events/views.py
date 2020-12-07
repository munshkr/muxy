import json
from urllib.parse import urlparse

from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from events.models import Stream


@require_POST
def on_publish(request):
    # nginx-rtmp makes the stream name available in the POST body via `name`
    stream_key = request.POST['name']

    # Lookup the activity and verify the publisher is allowed to stream.
    stream = get_object_or_404(Stream, stream_key=stream_key)

    now = timezone.now()

    # Check if stream is valid:
    # 1. Event is active
    # 2. Stream key is for current event slot
    if not stream.event.is_valid_at(now):
        return HttpResponseForbidden("Event is not active")
    if not stream.is_valid_at(now):
        return HttpResponseForbidden("Stream is not valid")

    # Set the stream live
    stream.live_at = now
    stream.save()

    return HttpResponse("OK")


@require_POST
def on_publish_done(request):
    # When a stream stops nginx-rtmp will still dispatch callbacks
    # using the original stream key, not the redirected stream name.
    stream_key = request.POST['name']

    # Set the stream offline
    Stream.objects.filter(stream_key=stream_key).update(live_at=None)

    # Response is ignored.
    return HttpResponse("OK")


@require_GET
def stream_options(request):
    stream_key = request.GET['key']
    stream = get_object_or_404(Stream, stream_key=stream_key)

    event = stream.event
    services = event.streamingservice_set.all()
    services = [
        dict(kind=s.kind, server=s.server, key=s.key) for s in services
    ]

    data = dict(name=event.name, services=services)
    return HttpResponse(json.dumps(data))
