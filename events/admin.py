from django.contrib import admin

from events.forms import StreamingServiceForm
from events.models import Event, Stream, Participant, StreamingService


class StreamingServiceInline(admin.TabularInline):
    model = StreamingService


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'url')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'starts_at', 'ends_at', 'active')
    inlines = [
        StreamingServiceInline,
    ]


class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_event_name', 'starts_at', 'ends_at',
                    'get_participant_name', 'live_at', 'stream_key')
    exclude = ('live_at', )

    def get_event_name(self, obj):
        return obj.event.name

    get_event_name.short_description = 'Event'
    get_event_name.admin_order_field = 'event__name'

    def get_participant_name(self, obj):
        return obj.participant.name

    get_participant_name.short_description = 'Participant'
    get_participant_name.admin_order_field = 'participant__name'

    def get_date_range(self, obj):
        return '{starts_at} - {obj.ends_at}'.format(starts_at=obj.starts_at,
                                                    ends_at=obj.ends_at)

    get_date_range.short_description = 'Date range'
    get_date_range.admin_order_field = ('starts_at', 'ends_at')


class StreamingServiceAdmin(admin.ModelAdmin):
    list_display = ('event', 'kind', 'server')
    form = StreamingServiceForm


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Stream, StreamAdmin)
admin.site.register(StreamingService, StreamingServiceAdmin)
