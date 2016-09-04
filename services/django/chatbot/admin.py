from django.contrib import admin

from chatbot.models import Message, Session, SessionData


class SessionDataInline(admin.TabularInline):
    model = SessionData
    readonly_fields = ("session", "key", "val")

    def has_add_permission(self, request):
        return False


class SessionAdmin(admin.ModelAdmin):
    readonly_fields = ("conv_id", "person", "finished")
    inlines = (SessionDataInline,)

admin.site.register(Session, SessionAdmin)

admin.site.register(Message)
