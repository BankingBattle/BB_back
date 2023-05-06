from typing import Optional

from rest_framework import status, serializers
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


def failed_validation_response(
        serializer: Optional[serializers.Serializer] = None,
        error: Optional[str] = None):
    fail_validation_reason = "Some of the provided data was incorrect"
    if not any([serializer, error]):
        raise ValueError(
            "At least one parameter should be provided: serializer or error")
    if error:
        fail_validation_reason = error
    elif serializer:
        fail_validation_reason = " ".join([
            f"{key}: {[value[:] for value in values][0]}"
            for key, values in serializer.errors.items()
        ])
    response_data: dict = dict(data=None,
                               success=False,
                               status_code=status.HTTP_400_BAD_REQUEST,
                               message=fail_validation_reason,
                               extra={})
    return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)
