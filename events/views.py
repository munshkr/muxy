from datetime import timedelta

from django.conf import settings
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ParseError
from rest_framework_api_key.permissions import HasAPIKey

from events.models import Event, Stream
from events.serializers import EventSerializer, StreamSerializer


class RtmpRedirect(HttpResponseRedirect):
    allowed_schemes = ['rtmp']


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all().order_by('-starts_at')
    permission_classes = [permissions.IsAuthenticated | HasAPIKey]
    filterset_fields = ('name', )


class StreamViewSet(viewsets.ModelViewSet):
    serializer_class = StreamSerializer
    queryset = Stream.objects.all().order_by('-event__starts_at', 'starts_at')
    permission_classes = [permissions.IsAuthenticated | HasAPIKey]
    filterset_fields = ('event__id', 'publisher_name', 'publisher_email',
                        'key')


@require_POST
def on_publish(request):
    # nginx-rtmp makes the stream name available in the POST body via `name`
    stream_key = request.POST['name']

    # Lookup the activity and verify the publisher is allowed to stream.
    stream = get_object_or_404(Stream, key=stream_key)

    now = timezone.now()

    # Check if stream is valid
    if not stream.is_valid_at(now):
        print("[PUBLISH] Stream is not valid at %s" % (now))
        return HttpResponseForbidden("Stream is not valid now")

    # If event has a custom RTMP URL, redirect to it
    if stream.event.rtmp_url:
        if stream.is_preparing_at(now):
            print(
                "[PUBLISH] Stream is preparing and not active yet. Allow but do not redirect."
            )
            return HttpResponse("OK")
        else:
            # Set the stream live
            stream.live_at = now
            stream.save()

            print("[PUBLISH] Stream is active. Allow and redirect.")
            return RtmpRedirect(stream.resolved_rtmp_url)
    else:
        print("[PUBLISH] Stream is active. Allow.")
        return HttpResponse("OK")


@require_POST
def on_publish_done(request):
    # When a stream stops nginx-rtmp will still dispatch callbacks
    # using the original stream key, not the redirected stream name.
    stream_key = request.POST['name']

    # Set the stream offline
    Stream.objects.filter(key=stream_key).update(live_at=None)

    # Response is ignored.
    print("[PUBLISH-DONE] Stream stopped streaming")
    return HttpResponse("OK")


@require_POST
def on_update(request):
    stream_key = request.POST['name']
    stream = get_object_or_404(Stream, key=stream_key)

    now = timezone.now()
    last_update = now - timedelta(seconds=settings.NGINX_RTMP_UPDATE_TIMEOUT)

    # nginx-rtmp only redirects when connecting for the first time. If publisher
    # is on "preparation", they are already streaming, so we need to forcibly
    # disconnect them, so that when they retry, they will be redirected at the
    # on_publish callback.
    if stream.is_preparing_at(last_update) and stream.is_active_at(now):
        print("[UPDATE] Stream was preparing and is now active. " \
              "Force disconnection to redirect to stream next time")
        return HttpResponseForbidden(
            "Stream was preparing and is now active. Retry")

    if not stream.is_valid_at(now):
        print("[UPDATE] Stream is not valid at %s" % (now))
        return HttpResponseForbidden("Stream is not valid now")

    return HttpResponse("OK")


@require_GET
def streams_check_key(request):
    stream_key = request.GET.get('key')
    if not stream_key:
        raise ParseError("Missing key parameter")

    stream = Stream.objects.filter(key=stream_key).first()
    if not stream:
        raise HttpResponse("There is no Stream with the key %s" %
                           (stream_key), )

    now = timezone.now()

    is_preparing = stream.is_preparing_at(now)
    is_active = stream.is_active_at(now)

    if is_preparing:
        begin, end = stream.preparing_range
        return HttpResponse(
            "Stream is preparing (%s). " \
            "You can start streaming now (from %s to %s), but stream will not be published to end server yet."
            % (now, begin, end))
    elif is_active:
        begin, end = stream.active_range
        return HttpResponse(
            "Stream is active now (%s). You can stream now! (from %s to %s)" %
            (now, begin, end))
    else:
        begin, end = stream.valid_range
        return HttpResponse(
            "Stream is not valid now (%s). You are allowed to stream from %s to %s"
            % (now, begin, end))
