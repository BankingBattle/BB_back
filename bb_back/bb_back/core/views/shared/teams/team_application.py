from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.constants import TeamApplicationStatusesEnum, TEAM_APPLICATION_STATUSES_NAMES
from bb_back.core.models import Game, TeamApplication
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    UserRolePermissionDeniedSerializer
from bb_back.core.views.utils.decorators import is_staff_user


# region create serializers
class CreateTeamApplicationRequestSerializer(serializers.Serializer):
    game_id = serializers.IntegerField(required=True)
    team_name = serializers.CharField(max_length=63, required=True)


class CreateTeamApplicationResponsePrivateSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class CreateTeamApplicationResponseSerializer(BaseResponseSerializer):
    response_data = CreateTeamApplicationResponsePrivateSerializer()


# endregion
# region get serializers
class TeamApplicationResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    game_id = serializers.IntegerField(required=True)
    game_name = serializers.CharField(max_length=63, required=True)
    team_name = serializers.CharField(max_length=63, required=True)
    applicant_email = serializers.CharField(max_length=63, required=True)
    status = serializers.ChoiceField(
        required=True, choices=list(TEAM_APPLICATION_STATUSES_NAMES.values()))


class GetTeamApplicationResponsePrivateSerializer(serializers.Serializer):
    applications = TeamApplicationResponseSerializer(many=True, required=False)


class GetTeamApplicationResponseSerializer(BaseResponseSerializer):
    response_data = GetTeamApplicationResponsePrivateSerializer()


# endregion
class TeamApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=CreateTeamApplicationRequestSerializer,
                         responses={
                             status.HTTP_200_OK:
                             CreateTeamApplicationResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    def post(self, request):
        request_data = CreateTeamApplicationRequestSerializer(
            data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        game = Game.objects.filter(id=data.get("game_id"),
                                   is_active=True).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {data.get('game_id')} does not exist."
            )
        if game.datetime_start and game.datetime_start < timezone.now():
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message="You can't register to a game that has already started."
            )
        if request.user.team and request.user.team.game.id == game.id:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=
                "You can't create new team application while being a part of another team."
            )
        if TeamApplication.objects.filter(game_id=data.get("game_id"),
                                          applicant=request.user,
                                          is_active=True,
                                          status=TeamApplicationStatusesEnum.
                                          STATUS_PENDING.value).exists():
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=
                "You have already created a team application for this game.")
        TeamApplication.objects.create(game=game,
                                       team_name=data.get("team_name"),
                                       applicant=request.user)
        response_data = CreateTeamApplicationResponseSerializer(
            data={"response_data": {
                "success": True
            }})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            "game_id",
            in_=openapi.IN_QUERY,
            description="Filter team applications within single game",
            type=openapi.TYPE_INTEGER,
            required=False,
        )
    ],
                         responses={
                             status.HTTP_200_OK:
                             GetTeamApplicationResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def get(self, request):
        filters = dict(is_active=True)
        if request.query_params.get("game_id"):
            filters.update(game_id=int(request.query_params.get("game_id")))
        team_applications = TeamApplication.objects.filter(**filters)
        application_schemas = [
            TeamApplicationResponseSerializer(
                data=dict(id=application.id,
                          game_id=application.game.id,
                          game_name=application.game.name,
                          team_name=application.team_name,
                          applicant_email=application.applicant.email,
                          status=TEAM_APPLICATION_STATUSES_NAMES.get(
                              application.status)))
            for application in team_applications
        ]
        application_data = []
        for app in application_schemas:
            app.is_valid()
            application_data.append(app.data)
        inner_data = GetTeamApplicationResponsePrivateSerializer(
            data={"applications": application_data})
        inner_data.is_valid(raise_exception=False)
        response_data = GetTeamApplicationResponseSerializer(
            data={"response_data": inner_data.data})
        response_data.is_valid(raise_exception=False)
        return Response(data=response_data.data, status=status.HTTP_200_OK)
