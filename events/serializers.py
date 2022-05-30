from rest_framework import serializers

from events.models import (Event, EventStreamURL, EventSupportURL, Stream,
                           StreamArchiveURL)


class EventStreamURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventStreamURL
        fields = ("url", "name")


class EventSupportURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventSupportURL
        fields = ("url", "name")


class EventSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="event-detail")
    event_url = serializers.CharField(source="url")
    stream_urls = EventStreamURLSerializer(many=True, read_only=True)
    support_urls = EventSupportURLSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"

    def validate(self, attrs):
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")

        if starts_at and ends_at:
            if ends_at < starts_at:
                raise serializers.ValidationError("event ends before starting")

            preparation_time = attrs.get("preparation_time")
            duration_in_minutes = (ends_at - starts_at).total_seconds() // 60
            if preparation_time and preparation_time > duration_in_minutes:
                raise serializers.ValidationError(
                    "preparation time (%d) is longer than the duration of the event (%d)"
                    % (preparation_time, duration_in_minutes)
                )

        return attrs


class PublicEventSerializer(EventSerializer):
    class Meta:
        model = Event
        exclude = ("rtmp_url",)


class StreamArchiveURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StreamArchiveURL
        fields = ("url", "name")


class StreamSerializer(serializers.HyperlinkedModelSerializer):
    recordings = serializers.SerializerMethodField()
    key = serializers.CharField(required=False)
    archive_urls = StreamArchiveURLSerializer(many=True, read_only=True)

    class Meta:
        model = Stream
        fields = "__all__"

    def get_recordings(self, stream):
        request = self.context.get("request")
        return [request.build_absolute_uri(path) for path in stream.recording_paths]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")
        key = attrs.get("key")

        if starts_at and ends_at:
            other_streams = Stream.objects.filter(
                event=attrs["event"],
                starts_at__lt=attrs["ends_at"],
                ends_at__gt=attrs["starts_at"],
            )
            if self.instance:
                other_streams = other_streams.exclude(pk=self.instance.pk)
            if key:
                other_streams = other_streams.exclude(key=attrs["key"])
            if other_streams.exists():
                events_str = [str(s) for s in other_streams.all()]
                raise serializers.ValidationError(
                    "overlaps with other streams: %s" % events_str
                )

        return attrs


class PublicStreamSerializer(StreamSerializer):
    recordings = None
    key = None

    class Meta:
        model = Stream
        exclude = ("key", "publisher_email")
