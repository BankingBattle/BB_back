import codecs
import csv

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, permissions
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
import os.path

from bb_back.core.models import Game
from bb_back.core.models import Round
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import (
    BaseResponseSerializer,
    BadRequestResponseSerializer,
    NotFoundResponseSerializer,
    UserRolePermissionDeniedSerializer,
)
from bb_back.core.views.utils.decorators import is_staff_user
from bb_back.settings import SUBMIT_MAX_SIZE, MEDIA_ROOT


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


class UploadRoundDataRequestSerializer(serializers.Serializer):
    data_of_round = serializers.FileField()


class UpdateRoundResponsePrivateSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()

    is_active = serializers.BooleanField()


class UploadRoundDataResponseSerializer(BaseResponseSerializer):
    response_data = serializers.FileField()


class RoundDataResponseSerializer(BaseResponseSerializer):
    response_data = serializers.FileField()


class UpdateRoundResponseSerializer(BaseResponseSerializer):
    response_data = UpdateRoundResponsePrivateSerializer()


class DeleteRoundResponsePrivateSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class DeleteRoundResponseSerializer(BaseResponseSerializer):
    response_data = DeleteRoundResponsePrivateSerializer()


class RoundView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

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
    @is_staff_user
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

    @swagger_auto_schema(request_body=UpdateRoundRequestSerializer,
                         responses={
                             status.HTTP_200_OK:
                             DeleteRoundResponsePrivateSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_404_NOT_FOUND:
                             NotFoundResponseSerializer,
                             status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def delete(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")
        round.is_active = False
        round.save()

        response_data = CreateRoundResponseSerializer(
            data={"response_data": {
                "success": True
            }})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class CreateRoundView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CreateRoundRequestSerializer,
        responses={status.HTTP_201_CREATED: CreateRoundResponseSerializer},
    )
    @is_staff_user
    def post(self, request):
        request_data = CreateRoundRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        round_schema = request_data.data
        game_req = Game.objects.filter(id=round_schema.get("game_id"))
        if not game_req:
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message="Game with this id does not exist.",
            )
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
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: RoundDataResponseSerializer}, )
    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()

        if not round:
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.",
            )

        if not round.data_of_round:
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} has no data.",
            )
        if not os.path.exists(
                os.path.join(MEDIA_ROOT, round.data_of_round.name)):
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} has no data.",
            )
        response_data = HttpResponse(round.data_of_round,
                                     content_type="application/vnd.ms-excel")

        response_data[
            "Content-Disposition"] = "inline; filename=" + round.data_of_round.name
        return response_data


class UploudRoundData(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="file",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={status.HTTP_200_OK: UploadRoundDataResponseSerializer},
    )
    def put(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()

        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")

        data_file = request.FILES.get("file")

        if data_file.size > SUBMIT_MAX_SIZE:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=f"File size {data_file.size} > {SUBMIT_MAX_SIZE}")

        round.data_of_round = data_file
        round.save()
        response_data = UploadRoundDataResponseSerializer(
            data={"response_data": {}})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class UploadRoundTargetView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="file",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={status.HTTP_200_OK: UploadRoundDataResponseSerializer},
    )
    @is_staff_user
    def post(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")

        file = request.FILES.get("file")
        try:
            csv_file = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
            for line in csv_file:
                line: dict
                if list(line.keys()) != ['id', 'fact', 'amount']:
                    raise ValueError(
                        'CSV file columns must be: "id", "fact", "amount"')
                if not all([value.isnumeric() for value in line.values()]):
                    raise ValueError(
                        'All provided values must be valid integers')
        except ValueError as ex:
            return response(status_code=status.HTTP_400_BAD_REQUEST,
                            data={},
                            message=f"{str(ex)}")
        if not file.name.endswith(".csv"):
            return response(status_code=status.HTTP_400_BAD_REQUEST,
                            data={},
                            message="Target file must have .csv extension")
        round.round_target = file
        round.save()
        response_data = UploadRoundDataResponseSerializer(
            data={"response_data": {}})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: RoundDataResponseSerializer}, )
    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")
        if not round.round_target:
            return response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"No target found for round {round.name}",
            )

        response_data = HttpResponse(round.round_target,
                                     content_type="application/vnd.ms-excel")
        response_data[
            "Content-Disposition"] = "inline; filename=" + round.round_target.name
        return response_data
