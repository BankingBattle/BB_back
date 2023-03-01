from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.constants import EmailTypes
from bb_back.core.models import User
from bb_back.core.utils import EmailSender, is_valid_email
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer
from bb_back.settings import ADMIN_KEY


class BaseRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.CharField(max_length=63)
    login = serializers.CharField(max_length=30)

    class Meta:
        fields = '__all__'


class RegistrationRequestSerializer(BaseRegistrationSerializer):
    password = serializers.CharField(max_length=30, min_length=8)
    admin_key = serializers.CharField(max_length=255,
                                      allow_null=True,
                                      required=False)


class RegistrationResponseSerializer(BaseResponseSerializer):
    response_data = BaseRegistrationSerializer()


class RegistrationUserView(APIView):
    serializer_class = RegistrationResponseSerializer

    @swagger_auto_schema(request_body=RegistrationRequestSerializer,
                         responses={
                             status.HTTP_200_OK:
                             RegistrationResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer
                         })
    def post(self, request):

        request_data = RegistrationRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
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
        if not is_valid_email(user_schema.get("email")):
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=
                f"Registration failed: email {user_schema.get('email')} is not valid."
            )
        hashed_password = make_password(user_schema.get('password'))
        is_valid_admin_key = user_schema.get("admin_key") == ADMIN_KEY
        user = User(first_name=user_schema.get("first_name"),
                    last_name=user_schema.get('last_name'),
                    login=user_schema.get('login'),
                    email=user_schema.get('email'),
                    password=hashed_password,
                    is_staff=is_valid_admin_key)
        user.save()
        EmailSender(to_users_emails=(user_schema.get('email'), ),
                    email_type=EmailTypes.NEW_USER_GREETING_EMAIL).send_email(
                        context=dict(email_verification_link=EmailSender.
                                     get_mail_verification_link(user=user)))
        response_data = RegistrationResponseSerializer(
            data={"response_data": user_schema})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
