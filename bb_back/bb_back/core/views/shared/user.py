from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.constants import EmailTypes
from bb_back.core.utils import EmailSender
from bb_back.core.utils.view_utils import failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer


class BaseUpdateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.CharField(max_length=63, required=False)


class UpdateUserRequestSerializer(BaseUpdateUserSerializer):
    password = serializers.CharField(max_length=63, required=False)

    class Meta:
        fields = '__all__'


class BaseGetUserResponseSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    email = serializers.CharField(max_length=63, required=True)
    login = serializers.CharField(max_length=30, required=True)
    is_email_confirmed = serializers.BooleanField(required=True)
    is_admin = serializers.BooleanField(required=False, allow_null=True)


class GetUserResponseSerializer(BaseResponseSerializer):
    response_data = BaseGetUserResponseSerializer()


class UpdateUserResponseSerializer(BaseResponseSerializer):
    response_data = BaseUpdateUserSerializer()


class UserView(APIView):
    serializer_class = UpdateUserResponseSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=UpdateUserRequestSerializer,
                         responses={
                             status.HTTP_200_OK:
                             UpdateUserResponseSerializer,
                             status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer
                         })
    def patch(self, request):
        user = request.user
        request_data = UpdateUserRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        if data.get("first_name"):
            user.first_name = data.get("first_name")
        if data.get("last_name"):
            user.last_name = data.get("last_name")
        if data.get("email"):
            user.email = data.get("email")
            user.is_email_confirmed = False
            EmailSender(
                to_users_emails=(data.get("email"), ),
                email_type=EmailTypes.VERIFY_NEW_MAIL_ADDRESS_EMAIL
            ).send_email(context=dict(
                email_verification_link=EmailSender.get_mail_verification_link(
                    user=user)))
        if data.get("password"):
            user.password = make_password(data.get("password"))
        user.save()

        response_data = UpdateUserResponseSerializer(
            data={
                "response_data": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                }
            })
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: GetUserResponseSerializer})
    def get(self, request):
        user = request.user
        response_data = GetUserResponseSerializer(data=dict(
            response_data=dict(first_name=user.first_name,
                               last_name=user.last_name,
                               email=user.email,
                               login=user.login,
                               is_email_confirmed=user.is_email_confirmed,
                               is_admin=user.is_staff)))
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
