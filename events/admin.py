from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from events.forms import StreamForm
from events.models import (
    Event,
    EventStreamURL,
    Stream,
    StreamNotification,
    CustomAPIKey,
)


class EventStreamURLInline(admin.TabularInline):
    model = EventStreamURL
    extra = 1


class CustomAPIKeyAdmin(APIKeyModelAdmin):
    list_display = [*APIKeyModelAdmin.list_display, "is_web"]
    search_fields = [*APIKeyModelAdmin.search_fields, "is_web"]


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "name", "url", "starts_at", "ends_at", "active")
    ordering = ("-starts_at",)
    inlines = [EventStreamURLInline]


class StreamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_event_name",
        "publisher_name",
        "starts_at",
        "ends_at",
        "live_at",
    )
    exclude = ("live_at",)
    form = StreamForm
    ordering = ("-starts_at",)
    list_filter = ("event",)

    def get_event_name(self, obj):
        return obj.event.name

    get_event_name.short_description = "Event"
    get_event_name.admin_order_field = "event__name"

    def get_date_range(self, obj):
        return "{starts_at} - {obj.ends_at}".format(
            starts_at=obj.starts_at, ends_at=obj.ends_at
        )

    get_date_range.short_description = "Date range"
    get_date_range.admin_order_field = ("starts_at", "ends_at")


class StreamNotificationAdmin(admin.ModelAdmin):
    list_display = ("stream", "kind", "sent_at")


admin.site.register(CustomAPIKey, CustomAPIKeyAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Stream, StreamAdmin)
admin.site.register(StreamNotification, StreamNotificationAdmin)
