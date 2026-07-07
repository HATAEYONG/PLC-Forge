from rest_framework import viewsets

from apps.alarms.models import Alarm
from apps.alarms.serializers import AlarmSerializer


class AlarmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
