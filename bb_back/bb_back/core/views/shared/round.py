from rest_framework import serializers, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.http import HttpResponse
from bb_back.core.utils.view_utils import response, failed_validation_response
import os

from bb_back.core.models import Round
from bb_back.core.models import Game
from bb_back.settings import MEDIA_ROOT
from bb_back.core.views.utils.base_serializers import (
    BaseResponseSerializer,
    BadRequestResponseSerializer,
    NotFoundResponseSerializer,
)


class CreateRoundRequestSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField(default=True)


class RoundRequestSerializer(serializers.Serializer):
    data_of_round = serializers.FileField()
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField()


class RoundResponseSerializer(BaseResponseSerializer):
    response_data = RoundRequestSerializer()


class CreateRoundResponseSerializer(BaseResponseSerializer):
    response_data = CreateRoundRequestSerializer()


class UpdateRoundRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=63, required=False)
    description = serializers.CharField(required=False)

    datetime_start = serializers.DateTimeField(required=False)
    datetime_end = serializers.DateTimeField(required=False)

    is_active = serializers.BooleanField(default=True)


class UpdateRoundResponsePrivateSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField()


class UpdateRoundResponseSerialier(BaseResponseSerializer):
    response_data = UpdateRoundResponsePrivateSerializer()


class RoundView(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: RoundResponseSerializer,
            status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
            status.HTTP_404_NOT_FOUND: NotFoundResponseSerializer,
        })
    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.",
            )

        response_data = RoundResponseSerializer(data=dict(response_data=dict(
            id=round.id,
            name=round.name,
            description=round.description,
            datetime_start=round.datetime_start,
            datetime_end=round.datetime_end,
            is_active=round.is_active,
            game_id=round.game_id,
        )))
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UpdateRoundRequestSerializer,
                         responses={
                             status.HTTP_200_OK: RoundResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_404_NOT_FOUND:
                             NotFoundResponseSerializer,
                         })
    def patch(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")
        request_data = UpdateRoundRequestSerializer(data=request.data)

        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        if data.get("name"):
            round.name = data.get("name")
        if data.get("description"):
            round.description = data.get("description")
        if data.get("datetime_start"):
            round.datetime_start = data.get("datetime_start")
        if data.get("datetime_end"):
            round.datetime_end = data.get("datetime_end")
        if data.get("is_active") is not None:
            round.is_active = data.get("is_active")
        round.save()

        response_data = RoundResponseSerializer(data=dict(response_data=dict(
            id=round.id,
            name=round.name,
            description=round.description,
            datetime_start=round.datetime_start,
            datetime_end=round.datetime_end,
            is_active=round.is_active,
            game_id=round.game_id,
        )))
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class CreateRoundView(APIView):

    @swagger_auto_schema(
        request_body=CreateRoundRequestSerializer,
        responses={status.HTTP_201_CREATED: CreateRoundResponseSerializer},
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
            data={"response_data": round_schema})
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=status.HTTP_201_CREATED)


class GetRoundDataView(APIView):

    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.",
            )
            # TODO Хардкод, требуется сделать эендпоинт загрузки файла и вывод по данным из поля самого объекта
        file_path = os.path.join(MEDIA_ROOT,
                                 f"round-data/{round.game_id}/{round_id}.txt")
        if not os.path.exists(file_path):
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Round with id = {round_id} has no data. Path to {file_path} does not exist",
            )

        file_stream = open(file_path, "rb")
        response_data = HttpResponse(file_stream.read(),
                                     content_type="application/vnd.ms-excel")
        response_data[
            "Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path)
        return response_data
