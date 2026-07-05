from django.contrib import admin

from .models import KnowledgeEdge


@admin.register(KnowledgeEdge)
class KnowledgeEdgeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("subject_type", "subject_id", "predicate", "object_type", "object_id", "user")
    list_filter = ("predicate", "subject_type", "object_type")
