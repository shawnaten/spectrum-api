from django.contrib import admin

from chatbot.models import Session, Message, SessionData


class SessionAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "person")


class SessionDataAdmin(admin.ModelAdmin):
    readonly_fields = ("session", "key", "val")


admin.site.register(Session, SessionAdmin)
admin.site.register(Message)
admin.site.register(SessionData, SessionDataAdmin)
