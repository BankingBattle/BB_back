from typing import Optional

from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response


def response(data: dict,
             message: Optional[str] = None,
             extra: Optional[dict] = None,
             status_code: Optional[int] = status.HTTP_200_OK,
             success: Optional[bool] = True):
    response_data = dict(data=data,
                         success=success,
                         status_code=status_code,
                         message=message,
                         extra=extra or {})
    return Response(data=response_data, status=status.HTTP_200_OK)


def parse_validation_error(ex: ValidationError):
    """
        Parses pydantic ValidationError
        :return: Error message string
        """
    first_error = ex.errors().pop()
    field = first_error['loc'][0],
    msg = first_error['msg']

    return f"Validation error: {field}: {msg}"
