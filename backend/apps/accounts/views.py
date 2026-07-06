from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import UserSerializer


class MeView(APIView):
    """현재 로그인한 사용자 정보."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)
