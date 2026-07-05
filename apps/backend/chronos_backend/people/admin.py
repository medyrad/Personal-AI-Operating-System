from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("display_name", "relationship_label", "user")
    list_filter = ("user",)
