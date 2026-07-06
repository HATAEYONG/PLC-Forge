from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.companies.urls")),
    path("api/", include("apps.projects.urls")),
    path("api/", include("apps.interview.urls")),
    path("api/", include("apps.requirements.urls")),
    path("api/", include("apps.knowledge.urls")),
    path("api/", include("apps.design.urls")),
    path("api/", include("apps.audit.urls")),
]
