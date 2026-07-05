from django.contrib import admin
from django.urls import path

from chronos_backend.ai.api import router as ai_router
from chronos_backend.events.api import api

api.add_router("/ai", ai_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
