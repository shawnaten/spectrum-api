from django.contrib import admin
from cal.models import Calendar, Event, EventSettings, RSVP, Checkin


class CalendarAdmin(admin.ModelAdmin):
    readonly_fields = ("name", "cal_id",)


class EventSettingsInline(admin.StackedInline):
    model = EventSettings
    readonly_fields = ("short_code",)

    def has_delete_permission(self, request, obj=None):
        return False


class RSVPInline(admin.TabularInline):
    model = RSVP


class CheckinInline(admin.TabularInline):
    model = Checkin


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ("calendar", "event_id", "location", "summary",
                       "description", "status", "start", "end", "recurring")
    inlines = (EventSettingsInline, RSVPInline, CheckinInline)

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)
