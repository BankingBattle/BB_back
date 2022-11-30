import binascii
import os

from django.core.cache import cache
from rest_framework.views import APIView
from pydantic import BaseModel, constr, ValidationError
from rest_framework import status

from bb_back.core.models import User
from django.contrib.auth.hashers import check_password

from bb_back.core.utils.view_utils import response, parse_validation_error


class LoginRequestSchema(BaseModel):
    login: constr(max_length=30)
    password: constr(max_length=30)


class LoginResponseSchema(BaseModel):
    access_token: str


class LoginUserView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def post(self, request):
        try:
            user_schema = LoginRequestSchema.parse_obj(request.data)
        except ValidationError as ex:
            return response(data={},
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message=parse_validation_error(ex))
        user = User.objects.filter(login=user_schema.login).first()
        if not user:
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"User with login {user_schema.login} not found")
        if not check_password(user_schema.password, user.hashed_pass):
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Unable to login: Wrong password provided")
        token = binascii.hexlify(os.urandom(20)).decode()
        cache.set(token, user.login)
        return response(data={111: token})
