from django.urls import path

from apps.generators.views import VendorGenerateView

urlpatterns = [
    path(
        "projects/<uuid:project_pk>/vendor-generate/",
        VendorGenerateView.as_view({"post": "create"}),
        name="project-vendor-generate",
    ),
]
