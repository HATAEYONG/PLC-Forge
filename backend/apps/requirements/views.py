from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.requirements import selectors, services
from apps.requirements.models import ProjectFact
from apps.requirements.serializers import FactTransitionSerializer, ProjectFactSerializer


class ProjectFactViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ProjectFact.objects.all()
    serializer_class = ProjectFactSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = selectors.facts_for_project(project_id=project_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fact = services.create_fact(**serializer.validated_data, actor=request.user)
        return Response(
            self.get_serializer(fact).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        fact = self.get_object()
        serializer = FactTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fact = services.transition_fact(
            fact=fact,
            new_status=serializer.validated_data["status"],
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(ProjectFactSerializer(fact).data)
