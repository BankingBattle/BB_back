from typing import List, Dict

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, permissions
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Game, Round, Submit, Team
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    NotFoundResponseSerializer, UserRolePermissionDeniedSerializer
from bb_back.core.views.utils.decorators import is_staff_user
from bb_back.settings import SUBMIT_MAX_SIZE


class GameRoundResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()


class GameLeaderboardResponseSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    place = serializers.IntegerField()
    points = serializers.IntegerField()
    is_current_team = serializers.BooleanField()


class TeamLeaderboardPosition:

    def __init__(self, id, name, points, is_current_team):
        self.id = id
        self.name = name
        self.points = points
        self.is_current_team = is_current_team


class ListGameResponsePrivateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    datetime_start = serializers.DateTimeField(allow_null=True, required=False)
    datetime_end = serializers.DateTimeField(allow_null=True, required=False)
    rounds = GameRoundResponseSerializer(many=True)
    leaderboard = GameLeaderboardResponseSerializer(many=True)


class ListGameResponseSerializer(BaseResponseSerializer):
    response_data = ListGameResponsePrivateSerializer(many=True)


class CreateGameRequestSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)

    datetime_start = serializers.DateTimeField(allow_null=True, required=False)
    datetime_end = serializers.DateTimeField(allow_null=True, required=False)


class CreateGameResponsePrivateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    datetime_start = serializers.DateTimeField(allow_null=False)
    datetime_end = serializers.DateTimeField(allow_null=False)


class CreateGameResponseSerializer(BaseResponseSerializer):
    response_data = CreateGameResponsePrivateSerializer()


class GetGameResponsePrivateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    datetime_start = serializers.DateTimeField(allow_null=False,
                                               required=False)
    datetime_end = serializers.DateTimeField(allow_null=False, required=False)
    rounds = GameRoundResponseSerializer(many=True)
    leaderboard = GameLeaderboardResponseSerializer(many=True)
    is_active = serializers.BooleanField(allow_null=True, required=False)
    participating = serializers.BooleanField(allow_null=False, required=False)


class GetGameResponseSerializer(BaseResponseSerializer):
    response_data = GetGameResponsePrivateSerializer()


class UploadGameLogoResponseSerializer(BaseResponseSerializer):
    response_data = serializers.JSONField(allow_null=True)


class UpdateGameRequestSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True,
                                        allow_blank=True,
                                        required=False)

    datetime_start = serializers.DateTimeField(allow_null=True, required=False)
    datetime_end = serializers.DateTimeField(allow_null=True, required=False)

    is_active = serializers.BooleanField(allow_null=True, required=False)


class UpdateGameResponseSerializer(GetGameResponseSerializer):
    ...


class GameViewsHandler:

    @staticmethod
    def get_game_rounds(game: Game) -> List[Dict]:
        game_rounds = Round.objects.filter(game=game, is_active=True)
        serialized_rounds = [
            GameRoundResponseSerializer(
                data=dict(id=round.id,
                          name=round.name,
                          description=round.description,
                          datetime_start=round.datetime_start,
                          datetime_end=round.datetime_end))
            for round in game_rounds
        ]
        for round_data in serialized_rounds:
            round_data.is_valid()
        return [round_data.data for round_data in serialized_rounds]

    @staticmethod
    def get_game_leaderboard(game: Game, current_team) -> List[Dict]:
        leaders = []
        if current_team is None:
            current_team_id = -1
        else:
            current_team_id = current_team.id

        for team in Team.objects.filter(game=game):
            score = GameViewsHandler.get_sum_score(team.id, game)
            team_position = TeamLeaderboardPosition(team.id, team.name, score,
                                                    team.id == current_team_id)
            leaders.append(team_position)

        leaders = sorted(leaders, reverse=True, key=lambda x: x.points)
        index = 1

        serialized_leaderBoard = []

        for elem in leaders:
            serialized_leaderBoard.append(
                GameLeaderboardResponseSerializer(
                    data=dict(name=elem.name,
                              id=elem.id,
                              place=index,
                              points=elem.points,
                              is_current_team=elem.is_current_team)))
            index += 1

        for leaderBoard_data in serialized_leaderBoard:
            leaderBoard_data.is_valid()
        return [
            leaderBoard_data.data
            for leaderBoard_data in serialized_leaderBoard
        ]

    @staticmethod
    def get_sum_score(id_command, game: Game):
        sum = 0.0
        rounds = Round.objects.filter(game=game)
        for round in rounds:
            last_submit = Submit.objects.filter(round_num=round.id,
                                                id_command=id_command,
                                                final=True).first()
            if not last_submit:
                last_submit = Submit.objects.filter(
                    round_num=round.id,
                    id_command=id_command).order_by('-created_at').first()
            if last_submit:
                sum += last_submit.score

        return sum


class CreateGameView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=CreateGameRequestSerializer,
                         responses={
                             status.HTTP_201_CREATED:
                             CreateGameResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def post(self, request):
        request_data = CreateGameRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        game_schema = request_data.data
        if Game.objects.filter(name=game_schema.get("name")).exists():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=(f'Game with name {game_schema.get("name")} ' +
                         'already exists'))
        game = Game.objects.create(
            name=game_schema.get("name"),
            description=game_schema.get("description"),
            datetime_start=game_schema.get("datetime_start"),
            datetime_end=game_schema.get("datetime_end"))

        response_data = CreateGameResponseSerializer(data=dict(
            response_data=dict(
                id=game.id,
                name=game.name,
                description=game.description,
                datetime_start=game.datetime_start,
                datetime_end=game.datetime_end,
            )))
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: ListGameResponseSerializer,
    })
    def get(self, request):
        games = Game.objects.filter(is_active=True)
        response_data = ListGameResponseSerializer(
            data={
                "response_data": [
                    dict(name=game.name,
                         id=game.id,
                         description=game.description,
                         datetime_start=game.datetime_start,
                         datetime_end=game.datetime_end,
                         rounds=GameViewsHandler.get_game_rounds(game=game),
                         leaderboard=GameViewsHandler.get_game_leaderboard(
                             game=game, current_team=request.user.team))
                    for game in games
                ]
            })
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class GameView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GetGameResponseSerializer,
            status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
            status.HTTP_404_NOT_FOUND: NotFoundResponseSerializer
        })
    def get(self, request, game_id):
        filters = dict(id=game_id)
        if not request.user.is_staff:
            filters.update(is_active=True)
        game = Game.objects.filter(**filters).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.")
        game_rounds = GameViewsHandler.get_game_rounds(game=game)
        game_leaderboard = GameViewsHandler.get_game_leaderboard(
            game=game, current_team=request.user.team)
        participants_of_current_user = False
        if request.user.team is not None:
            participants_of_current_user = request.user.team.game == game
        inner_response = dict(id=game.id,
                              name=game.name,
                              description=game.description,
                              rounds=game_rounds,
                              leaderboard=game_leaderboard,
                              datetime_start=game.datetime_start,
                              datetime_end=game.datetime_end,
                              is_active=game.is_active,
                              participating=participants_of_current_user)
        response_data = GetGameResponseSerializer(
            data={"response_data": inner_response})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UpdateGameRequestSerializer,
                         responses={
                             status.HTTP_200_OK:
                             UpdateGameResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def patch(self, request, game_id):
        game = Game.objects.filter(id=game_id).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.")

        request_data = UpdateGameRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        if data.get("name"):
            game.name = data.get("name")
        if data.get("description"):
            game.description = data.get("description")
        if data.get("datetime_start"):
            game.datetime_start = data.get("datetime_start")
        if data.get("datetime_end"):
            game.datetime_end = data.get("datetime_end")
        if data.get("is_active") is not None:
            game.is_active = data.get("is_active")
        game.save()

        inner_response = dict(
            name=game.name,
            description=game.description,
            rounds=GameViewsHandler.get_game_rounds(game=game),
            leaderboard=GameViewsHandler.get_game_leaderboard(
                game=game, current_team=request.user.team),
            datetime_start=game.datetime_start,
            datetime_end=game.datetime_end,
        )
        response_data = UpdateGameResponseSerializer(
            data={"response_data": inner_response})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class GameLogoView(APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]
    permission_classes = (permissions.IsAuthenticated, )

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
        responses={status.HTTP_200_OK: UploadGameLogoResponseSerializer},
    )
    @is_staff_user
    def put(self, request, game_id):
        game = Game.objects.filter(id=game_id).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.")
        logo_file = request.FILES.get("file")
        if logo_file.size > SUBMIT_MAX_SIZE:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=f"File size {logo_file.size} > {SUBMIT_MAX_SIZE}")
        game.logo = logo_file
        game.save()

        response_data = UploadGameLogoResponseSerializer(
            data={"response_data": {}})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    def get(self, request, game_id):
        game = Game.objects.filter(id=game_id).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.")
        if not game.logo:
            return response(status_code=status.HTTP_404_NOT_FOUND,
                            data={},
                            message=f"Game with id = {game_id} has no logo")
        filename = game.logo.name.split('/')[-1]
        resp = HttpResponse(game.logo, content_type='text/plain')
        resp['Content-Disposition'] = f'attachment; filename={filename}'

        return resp
