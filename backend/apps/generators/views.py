from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.generators.services import generate_vendor_package
from apps.projects.models import Project


class VendorGenerateView(viewsets.ViewSet):
    """POST /api/projects/{project_pk}/vendor-generate/?vendor=ls"""

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        vendor = request.query_params.get("vendor", "ls")
        result = generate_vendor_package(project=project, vendor=vendor, actor=request.user)
        return Response(
            {
                "vendor": result["vendor"],
                "files": result["files"],
                "mapping_report": result["mapping_report"],
            },
            status=status.HTTP_201_CREATED,
        )
