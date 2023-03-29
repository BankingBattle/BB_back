from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, permissions, status as django_status
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Team, User
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    UserRolePermissionDeniedSerializer
from bb_back.core.views.utils.decorators import is_staff_user


class UserTeamResponseSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=30, required=True)
    email = serializers.CharField(max_length=64, required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)


class TeamResponseSerializer(serializers.Serializer):
    game = serializers.CharField(max_length=64, required=True)
    name = serializers.CharField(max_length=64, required=True)
    description = serializers.CharField(max_length=255, required=True)
    users = UserTeamResponseSerializer(many=True, required=False)


class GetTeamListViewResponsePrivateSerializer(serializers.Serializer):
    teams = TeamResponseSerializer(many=True, required=False)


class GetTeamListViewResponseSerializer(BaseResponseSerializer):
    response_data = GetTeamListViewResponsePrivateSerializer()


class GetCurrentTeamInfoResponseSerializer(BaseResponseSerializer):
    response_data = TeamResponseSerializer()


class PatchCurrentTeamInfoResponseSerializer(
        GetCurrentTeamInfoResponseSerializer):
    ...


class PatchCurrentTeamRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, required=True)
    description = serializers.CharField(max_length=255, required=True)


class CurrentTeamView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            django_status.HTTP_200_OK: GetCurrentTeamInfoResponseSerializer,
            django_status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
            django_status.HTTP_403_FORBIDDEN:
            UserRolePermissionDeniedSerializer
        })
    def get(self, request):
        user_team = request.user.team
        if not user_team:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Current user {request.user.email} does not have a team")
        team_info = _team_to_response(user_team)
        response_data = GetCurrentTeamInfoResponseSerializer(
            data={"response_data": team_info})
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=django_status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PatchCurrentTeamRequestSerializer,
                         responses={
                             django_status.HTTP_200_OK:
                             PatchCurrentTeamInfoResponseSerializer,
                             django_status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             django_status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    def patch(self, request):
        request_data = PatchCurrentTeamRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        user_team = request.user.team
        if not user_team:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Current user {request.user.email} does not have a team")
        user_team.name = data.get("name") if data.get(
            "name") else user_team.name
        user_team.description = data.get("description") if data.get(
            "description") else user_team.description
        user_team.save()

        team_info = _team_to_response(user_team)
        response_data = PatchCurrentTeamInfoResponseSerializer(
            data={"response_data": team_info})
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=django_status.HTTP_200_OK)


class TeamListView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            "game_id",
            in_=openapi.IN_QUERY,
            description="Filter teams within single game",
            type=openapi.TYPE_INTEGER,
            required=False,
        )
    ],
                         responses={
                             django_status.HTTP_200_OK:
                             GetTeamListViewResponseSerializer,
                             django_status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             django_status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def get(self, request):
        filters = dict(is_active=True)
        if request.query_params.get("game_id"):
            filters.update(game_id=int(request.query_params.get("game_id")))
        teams = Team.objects.filter(**filters)
        teams = [_team_to_response(team) for team in teams]
        response_data = GetTeamListViewResponseSerializer(
            data={"response_data": dict(teams=teams)})
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=django_status.HTTP_200_OK)


def _team_to_response(team: Team):
    users = User.objects.filter(team=team)
    user_schemas = [
        UserTeamResponseSerializer(data=dict(login=user.login,
                                             email=user.email,
                                             first_name=user.first_name,
                                             last_name=user.last_name))
        for user in users
    ]
    for user in user_schemas:
        user.is_valid()
    team_data = TeamResponseSerializer(
        data=dict(game=team.game.name if team.game else None,
                  name=team.name,
                  description=team.description,
                  users=[user.data for user in user_schemas]))
    team_data.is_valid()
    return team_data.data
