from django.contrib import admin

from events.forms import StreamForm
from events.models import SlotInterval, Event, Stream, StreamNotification
from django.forms.models import BaseInlineFormSet


class SlotIntervalInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = [{
            'starts_at': kwargs['instance'].starts_at,
            'ends_at': kwargs['instance'].ends_at
        }]
        super(SlotIntervalInlineFormSet, self).__init__(*args, **kwargs)


class SlotIntervalInline(admin.TabularInline):
    model = SlotInterval
    extra = 1
    formset = SlotIntervalInlineFormSet


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name', 'url', 'starts_at', 'ends_at',
                    'active')
    ordering = ('-starts_at', )
    inlines = [
        SlotIntervalInline,
    ]


class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_event_name', 'publisher_name', 'starts_at',
                    'ends_at', 'live_at')
    exclude = ('live_at', )
    form = StreamForm
    ordering = ('-starts_at', )
    list_filter = ('event', )

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