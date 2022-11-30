from rest_framework.views import APIView
from pydantic import BaseModel, constr, ValidationError
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password

from bb_back.core.models import User

from bb_back.core.utils.view_utils import response, parse_validation_error


class RegistrationRequestSchema(BaseModel):
    first_name: constr(max_length=30)
    last_name: constr(max_length=30)
    email: constr(max_length=63)
    login: constr(max_length=30)
    password: constr(max_length=30)


class RegistrationResponseSchema(BaseModel):
    ...


class RegistrationUserView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

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
                    hashed_pass=hashed_password)
        user.save()
        return response(data=user_schema.dict(),
                        message="User succesfully created")
