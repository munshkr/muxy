from django.contrib import admin

from events.forms import StreamForm
from events.models import Event, Stream, StreamNotification


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'starts_at', 'ends_at', 'active')
    ordering = ('-starts_at',)


class StreamAdmin(admin.ModelAdmin):
    list_display = ('slug', 'get_event_name', 'starts_at', 'ends_at',
                    'publisher_name', 'publisher_email', 'live_at', 'key')
    list_display_links = ('slug', )
    exclude = ('live_at', )
    form = StreamForm
    ordering = ('starts_at',)
    list_filter = ('event',)

    def get_event_name(self, obj):
        return obj.event.name

    get_event_name.short_description = 'Event'
    get_event_name.admin_order_field = 'event__name'

    def get_date_range(self, obj):
        return '{starts_at} - {obj.ends_at}'.format(starts_at=obj.starts_at,
                                                    ends_at=obj.ends_at)

    get_date_range.short_description = 'Date range'
    get_date_range.admin_order_field = ('starts_at', 'ends_at')


class StreamNotificationAdmin(admin.ModelAdmin):
    list_display = ('stream', 'kind', 'sent_at')


admin.site.register(Event, EventAdmin)
admin.site.register(Stream, StreamAdmin)
admin.site.register(StreamNotification, StreamNotificationAdmin)
