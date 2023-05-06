from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from bb_back.core.models import User


class AppHealthCheckView(APIView):

    def get(self, request):

        return Response(data=dict(success=True), status=status.HTTP_200_OK)


class DBHealthCheckView(APIView):

    def get(self, request):
        User.objects.first()
        return Response(data=dict(success=True), status=status.HTTP_200_OK)
