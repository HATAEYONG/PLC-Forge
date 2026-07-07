from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from apps.documents.export import export_project_xlsx
from apps.projects.models import Project

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class ExportView(viewsets.ViewSet):
    """GET /api/projects/{project_pk}/export/ — 설계 산출물 Excel 다운로드."""

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        content = export_project_xlsx(project)
        response = HttpResponse(content, content_type=XLSX_CONTENT_TYPE)
        filename = f"PLC-Forge_{project.code}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
