from django.urls import path

from apps.documents.views import ExportView

urlpatterns = [
    path(
        "projects/<uuid:project_pk>/export/",
        ExportView.as_view({"get": "list"}),
        name="project-export",
    ),
]
