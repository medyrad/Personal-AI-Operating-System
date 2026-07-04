from django.contrib import admin

from .models import Event, TaskDetail


class TaskDetailInline(admin.StackedInline):  # type: ignore[type-arg]
    model = TaskDetail
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("title", "type", "user", "occurred_at", "importance")
    list_filter = ("type", "user")
    inlines = [TaskDetailInline]
