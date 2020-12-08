from rest_framework import serializers

from events.models import Event, Stream


class EventSerializer(serializers.HyperlinkedModelSerializer):
    def validate(self, attrs):
        pass

    class Meta:
        model = Event
        fields = '__all__'


class StreamSerializer(serializers.HyperlinkedModelSerializer):
    def validate(self, attrs):
        pass

    class Meta:
        model = Stream
        fields = '__all__'
