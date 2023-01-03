from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import User
from bb_back.core.utils.view_utils import response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class BaseRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.CharField(max_length=63)
    login = serializers.CharField(max_length=30)

    class Meta:
        fields = '__all__'


class RegistrationRequestSerializer(BaseRegistrationSerializer):
    password = serializers.CharField(max_length=30)


class RegistrationResponseSerializer(BaseResponseSerializer):
    response_data = BaseRegistrationSerializer()


class RegistrationUserView(APIView):
    serializer_class = RegistrationResponseSerializer

    @swagger_auto_schema(
        request_body=RegistrationRequestSerializer,
        responses={status.HTTP_200_OK: RegistrationResponseSerializer})
    def post(self, request):

        request_data = RegistrationRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return response(data={},
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message="Provided data not valid")
        user_schema = request_data.data
        if User.objects.filter(login=user_schema.get("login")).exists():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=(f"User with login {user_schema.get('login')} " +
                         "already exists"))
        if User.objects.filter(email=user_schema.get("email")).exists():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=(f"User with email {user_schema.get('email')} " +
                         "already exists"))
        hashed_password = make_password(user_schema.get('password'))

        user = User(first_name=user_schema.get("first_name"),
                    last_name=user_schema.get('last_name'),
                    login=user_schema.get('login'),
                    email=user_schema.get('email'),
                    password=hashed_password)
        user.save()
        response_data = RegistrationResponseSerializer(
            data={"response_data": user_schema})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
