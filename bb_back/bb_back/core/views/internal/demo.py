from rest_framework.response import Response
from rest_framework.views import APIView


class DemoView(APIView):

    def get(self, request, status):
        return Response(data=dict(success=True), status=int(status))
