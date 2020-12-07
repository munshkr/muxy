import json
from urllib.parse import urlparse

from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from events.models import EventSlot


@require_POST
def on_publish(request):
    # nginx-rtmp makes the stream name available in the POST body via `name`
    stream_key = request.POST['name']

    # Lookup the stream and verify the publisher is allowed to stream.
    stream = get_object_or_404(EventSlot, stream_key=stream_key)

    # Check if stream is valid:
    # 1. Stream key is for current event slot
    # 2. Event is active
    # if not stream.user.is_active:
    # return HttpResponseForbidden("Stream key is not currently valid")

    # Set the stream live
    stream.live_at = timezone.now()
    stream.save()

    # # Redirect to the event RTMP server
    # parsed = urlparse(stream.event.rtmp_url)
    # replaced = parsed._replace(scheme='http')
    # url = replaced.geturl()
    # print("URL:", url)

    # return HttpResponseRedirect(url)

    print("API: Publish OK")
    return HttpResponse("OK")


@require_POST
def on_publish_done(request):
    # When a stream stops nginx-rtmp will still dispatch callbacks
    # using the original stream key, not the redirected stream name.
    stream_key = request.POST['name']

    # Set the stream offline
    EventSlot.objects.filter(stream_key=stream_key).update(live_at=None)

    # Response is ignored.
    return HttpResponse("OK")


@require_GET
def stream_options(request):
    stream_key = request.GET['key']
    stream = get_object_or_404(EventSlot, stream_key=stream_key)

    event = stream.event
    services = event.streamingservice_set.all()
    services = [
        dict(kind=s.kind, server=s.server, key=s.key) for s in services
    ]

    data = dict(name=event.name, services=services)
    return HttpResponse(json.dumps(data))
