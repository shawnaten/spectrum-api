from django.contrib import admin
from cal.models import Calendar, Event, EventSettings, RSVP, Checkin


class CalendarAdmin(admin.ModelAdmin):
    readonly_fields = ("name", "cal_id",)


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ("calendar", "event_id", "location", "summary",
                       "description", "status", "start", "end", "recurring")


class EventSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("event", "short_code")


class RSVPAdmin(admin.ModelAdmin):
    readonly_fields = ("event", "person")


class CheckinAdmin(admin.ModelAdmin):
    readonly_fields = ("event", "person")

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventSettings, EventSettingsAdmin)
admin.site.register(RSVP, RSVPAdmin)
admin.site.register(Checkin, CheckinAdmin)
