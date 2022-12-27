from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status

from bb_back.core.models.game import Game

from bb_back.core.utils.view_utils import response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class GameRequestSerializer(serializers.Serializer):
    Name = serializers.CharField(max_length=30)
    # Organizater = models.ForeignKey(User, on_delete=models.CASCADE)
    # created_at = serializers.DateTimeField(default=datetime.now())
    # players = .ManyToManyField(User)
    # finish_at = serializers.DateTimeField(default=datetime.now() + timedelta(days=1))
    is_active = serializers.BooleanField(default=True)


class GameResponseSerializer(BaseResponseSerializer):
    response_data = GameRequestSerializer()


# class GameRequestSerializer(GameSerializer):
#    password = serializers.CharField(max_length=30)


class GameView(APIView):
    @swagger_auto_schema(
        request_body=GameRequestSerializer,
        responses={status.HTTP_200_OK: GameResponseSerializer},
    )
    def post(self, request):
        # request_data = RegistrationRequestSerializer(data=request.data)
        request_data = GameRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Provided data not valid",
            )
        game_schema = request_data.data

        user = Game(
            first_name=game_schema.get("first_name"),
            last_name=game_schema.get("last_name"),
            login=game_schema.get("login"),
            email=game_schema.get("email"),
        )
        Game.save()
        response_data = GameResponseSerializer(data={"response_data": game_schema})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
