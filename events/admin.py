from django.contrib import admin

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'starts_at', 'ends_at', 'active')


admin.site.register(Event, EventAdmin)
