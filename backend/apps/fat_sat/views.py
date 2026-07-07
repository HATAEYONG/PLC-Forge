from rest_framework import mixins, viewsets

from apps.fat_sat.models import TestCase
from apps.fat_sat.serializers import TestCaseSerializer


class TestCaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """테스트 케이스 조회 + 실행 결과 기록(actual_result/status 등 수정 허용)."""

    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        phase = self.request.query_params.get("phase")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if phase:
            queryset = queryset.filter(phase=phase.upper())
        return queryset
