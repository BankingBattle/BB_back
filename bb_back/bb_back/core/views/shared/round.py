from rest_framework import serializers, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from django.http import HttpResponse
from bb_back.core.utils.view_utils import failed_validation_response
import os

from bb_back.core.models import Round
from bb_back.core.models import Game
from bb_back.settings import SUBMIT_MAX_SIZE
from bb_back.settings import MEDIA_ROOT
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class CreateRoundRequestSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField(default=True)


class RoundRequestSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField(default=True)

    data = serializers.FileField()


class RoundResponseSerializer(BaseResponseSerializer):
    response_data = RoundRequestSerializer()


class CreateRoundResponseSerializer(BaseResponseSerializer):
    response_data = CreateRoundRequestSerializer()


class RoundView(APIView):
    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        response_data = RoundResponseSerializer(
            data=dict(
                response_data=dict(
                    id=round.id,
                    name=round.name,
                    description=round.description,
                    datetime_start=round.datetime_start,
                    datetime_end=round.datetime_end,
                    is_active=round.is_active,
                    game_id=round.game_id,
                )
            )
        )
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class CreateRoundView(APIView):
    @swagger_auto_schema(
        request_body=CreateRoundRequestSerializer,
        responses={status.HTTP_200_OK: CreateRoundResponseSerializer},
    )
    def post(self, request):
        request_data = CreateRoundRequestSerializer(data=request.data)

        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        round_schema = request_data.data
        Round.objects.create(
            name=round_schema.get("name"),
            game=Game.objects.get(id=round_schema.get("game_id")),
            description=round_schema.get("description"),
            datetime_start=round_schema.get("datetime_start"),
            datetime_end=round_schema.get("datetime_end"),
            is_active=round_schema.get("is_active"),
        )
        response_data = CreateRoundResponseSerializer(
            data={"response_data": round_schema}
        )
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_201_CREATED)


class GetRoundDataView(APIView):
    def get(self, request, round_id):
        round = Round.objects.get(id=round_id)
        file_path = os.path.join(
            MEDIA_ROOT, f"round_data/{round.game_id}/{round_id}.txt"
        )
        if os.path.exists(file_path):
            fh = open(file_path, "rb")
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST, data=file_path)
