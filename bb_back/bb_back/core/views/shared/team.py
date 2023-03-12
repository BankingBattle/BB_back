from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers, permissions
from drf_yasg.utils import swagger_auto_schema

from bb_back.core.models import Team, User, Game
from bb_back.core.views.utils.base_serializers import (
    BaseResponseSerializer,
    BadRequestResponseSerializer,
    NotFoundResponseSerializer,
)
from bb_back.core.utils.view_utils import failed_validation_response, response


class CreateTeamRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=15)
    description = serializers.CharField(max_length=255,
                                        allow_null=True,
                                        required=False)
    game_id = serializers.IntegerField()


class CreateTeamResponseSerializer(BaseResponseSerializer):
    response_data = CreateTeamRequestSerializer()


class TeamView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CreateTeamRequestSerializer,
        responses={status.HTTP_201_CREATED: CreateTeamResponseSerializer})
    def post(self, request):
        request_data = CreateTeamRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        validated_data = request_data.validated_data
        game_id = validated_data['game_id']
        game = Game.objects.filter(id=game_id).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.",
            )
        team = Team.objects.create(
            name=validated_data['name'],
            description=validated_data.get('description'),
            leader=request.user,
            game=game)
        members = [request.user]
        team.members.set(members)
        team.save()
        response_data = CreateTeamResponseSerializer(
            data={"response_data": request_data.data})
        response_data.is_valid()
        return Response(response_data.data, status=status.HTTP_201_CREATED)
