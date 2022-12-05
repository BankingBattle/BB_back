from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from pydantic import BaseModel, ValidationError, Field
from rest_framework import status
from django.contrib.auth.hashers import make_password

from bb_back.core.models import User

from bb_back.core.utils.view_utils import response, parse_validation_error


class BaseRegistrationRequestSchema(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)
    email: str = Field(..., max_length=63)
    login: str = Field(..., max_length=30)
    password: str = Field(..., max_length=30)


class RegistrationRequestSchema(BaseRegistrationRequestSchema):
    password: str = Field(..., max_length=30)


class RegistrationResponseSchema(BaseRegistrationRequestSchema):
    ...


class RegistrationUserView(APIView):
    @swagger_auto_schema(method='post', request_body={})
    @api_view(['POST'])
    def post(self, request):
        """
        Return a list of all users.
        """
        try:
            user_schema = RegistrationRequestSchema.parse_obj(request.data)
        except ValidationError as ex:
            return response(data={},
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message=parse_validation_error(ex))
        if User.objects.filter(login=user_schema.login).exists():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"User with login {user_schema.login} already exists")
        if User.objects.filter(email=user_schema.email).exists():
            return response(
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"User with email {user_schema.email} already exists")
        hashed_password = make_password(user_schema.password)

        user = User(first_name=user_schema.first_name,
                    last_name=user_schema.last_name,
                    login=user_schema.login,
                    email=user_schema.email,
                    password=hashed_password)
        user.save()
        response_data = RegistrationResponseSchema(**user_schema.dict())
        return response(data=response_data.dict(),
                        message="User succesfully created")
