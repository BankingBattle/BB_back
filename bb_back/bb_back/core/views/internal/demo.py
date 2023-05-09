from rest_framework import status as drf_status
from rest_framework.response import Response
from rest_framework.views import APIView


class DemoView(APIView):

    def get(self, request, status):

        return Response(data={}, status=drf_status.HTTP_405_METHOD_NOT_ALLOWED)
