from typing import List, Dict

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Game, Round
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    NotFoundResponseSerializer


class GameRoundResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=False)
    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()


class GameLeaderboardResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    place = serializers.IntegerField()
    points = serializers.IntegerField()
    is_current_team = serializers.BooleanField()


class ListGameResponsePrivateSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    rounds = GameRoundResponseSerializer(many=True)
    leaderboard = GameLeaderboardResponseSerializer(many=True)


class ListGameResponseSerializer(BaseResponseSerializer):
    response_data = ListGameResponsePrivateSerializer(many=True)


class CreateGameRequestSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)


class CreateGameResponsePrivateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)


class CreateGameResponseSerializer(BaseResponseSerializer):
    response_data = CreateGameResponsePrivateSerializer()


class GetGameResponsePrivateSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    rounds = GameRoundResponseSerializer(many=True)
    leaderboard = GameLeaderboardResponseSerializer(many=True)


class GetGameResponseSerializer(BaseResponseSerializer):
    response_data = GetGameResponsePrivateSerializer()


class GameViewsHandler:

    @staticmethod
    def get_game_rounds(game: Game) -> List[GameRoundResponseSerializer]:
        game_rounds = Round.objects.filter(game=game)
        serialized_rounds = [
            GameRoundResponseSerializer(
                data=dict(id=round.id,
                          name=round.name,
                          datetime_start=round.datetime_start,
                          datetime_end=round.datetime_end))
            for round in game_rounds
        ]
        return serialized_rounds

    @staticmethod
    def get_game_leaderboard(game: Game) -> List[Dict]:
        # TODO hardcode
        return [{
            "name": "Test team №1",
            "id": 1,
            "place": 1,
            "points": 1234,
            "is_current_team": False
        }, {
            "name": "Test team №1",
            "id": 2,
            "place": 2,
            "points": 234,
            "is_current_team": True
        }, {
            "name": "Test team №1",
            "id": 3,
            "place": 3,
            "points": 34,
            "is_current_team": False
        }]


class CreateGameView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=CreateGameRequestSerializer,
                         responses={
                             status.HTTP_201_CREATED:
                             CreateGameResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer
                         })
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
        game = Game.objects.create(name=game_schema.get("name"),
                                   description=game_schema.get("description"))

        response_data = CreateGameResponseSerializer(data=dict(
            response_data=dict(
                id=game.id,
                name=game.name,
                description=game.description,
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
                         description=game.description,
                         rounds=GameViewsHandler.get_game_rounds(game=game),
                         leaderboard=GameViewsHandler.get_game_leaderboard(
                             game=game)) for game in games
                ]
            })
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


class GetGameView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GetGameResponseSerializer,
            status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
            status.HTTP_404_NOT_FOUND: NotFoundResponseSerializer
        })
    def get(self, request, game_id):
        game = Game.objects.filter(id=game_id).first()
        if not game:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Game with id = {game_id} does not exist.")
        game_rounds = GameViewsHandler.get_game_rounds(game=game)
        game_leaderboard = GameViewsHandler.get_game_leaderboard(game=game)
        inner_response = dict(name=game.name,
                              description=game.description,
                              rounds=game_rounds,
                              leaderboard=game_leaderboard)
        response_data = GetGameResponseSerializer(
            data={"response_data": inner_response})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)