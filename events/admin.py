from django.contrib import admin

from events.models import Event, EventSlot, Participant


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'url')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'starts_at', 'ends_at', 'active')


class EventSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_event_name', 'starts_at', 'ends_at',
                    'get_participant_name')

    def get_event_name(self, obj):
        return obj.event.name

    get_event_name.short_description = 'Event'
    get_event_name.admin_order_field = 'event__name'

    def get_participant_name(self, obj):
        return obj.participant.name

    get_participant_name.short_description = 'Participant'
    get_participant_name.admin_order_field = 'participant__name'

    def get_date_range(self, obj):
        return f'{obj.starts_at} - {obj.ends_at}'

    get_date_range.short_description = 'Date range'
    get_date_range.admin_order_field = ('starts_at', 'ends_at')


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventSlot, EventSlotAdmin)
