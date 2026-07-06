from rest_framework import viewsets

from apps.knowledge.models import KnowledgeItem
from apps.knowledge.serializers import KnowledgeItemSerializer


class KnowledgeItemViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer
