from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status

from bb_back.core.models.game import Game

from bb_back.core.utils.view_utils import response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class GameView(APIView):
    #   @swagger_auto_schema(
    #       request_body=RegistrationRequestSerializer,
    #       responses={status.HTTP_200_OK: RegistrationResponseSerializer})
    def post(self, request):
        # request_data = RegistrationRequestSerializer(data=request.data)
        return response(
            data={},
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Provided data not valid",
        )
