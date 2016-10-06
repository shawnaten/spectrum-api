from django.contrib import admin

from roster.models import Person


class PersonAdmin(admin.ModelAdmin):
    readonly_fields = ("phone", "created", "modified", "self_filled",
                       "self_updated")

admin.site.register(Person, PersonAdmin)
