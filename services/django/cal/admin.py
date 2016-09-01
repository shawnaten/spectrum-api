from django.contrib import admin
from cal.models import Calendar, Event, RSVPSettings, RSVP


class CalendarAdmin(admin.ModelAdmin):
    readonly_fields = ("name", "cal_id", "page_token", "sync_token")


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ("calendar", "event_id", "location", "summary",
                       "description", "status", "start", "end", "recurring",
                       "checkin_code")


class RSVPSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("event",)


class RSVPAdmin(admin.ModelAdmin):
    readonly_fields = ("event", "person")

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(RSVPSettings, RSVPSettingsAdmin)
admin.site.register(RSVP, RSVPAdmin)
