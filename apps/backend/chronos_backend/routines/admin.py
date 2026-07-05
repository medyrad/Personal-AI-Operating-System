from django.contrib import admin

from .models import Routine, RoutineOccurrence


class OccurrenceInline(admin.TabularInline):  # type: ignore[type-arg]
    model = RoutineOccurrence
    extra = 0


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "category", "schedule_rule", "active", "user")
    inlines = [OccurrenceInline]
