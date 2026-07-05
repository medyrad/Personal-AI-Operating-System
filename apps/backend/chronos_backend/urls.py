from django.contrib import admin
from django.urls import path

from chronos_backend.ai.api import router as ai_router
from chronos_backend.events.api import api
from chronos_backend.knowledge.api import router as knowledge_router
from chronos_backend.people.api import router as people_router
from chronos_backend.routines.api import router as routines_router

api.add_router("/ai", ai_router)
api.add_router("/routines", routines_router)
api.add_router("/knowledge", knowledge_router)
api.add_router("/people", people_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
