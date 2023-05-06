from rest_framework import serializers, status


class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)
    message = serializers.CharField(default=None, required=False)
    extra = serializers.JSONField(default={})

    class Meta:
        fields = [
            'response_data', 'success', 'status_code', 'message', 'extra'
        ]


class BadRequestResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    status_code = serializers.IntegerField(default=status.HTTP_400_BAD_REQUEST)
    message = serializers.CharField(default=None, required=False)
    extra = serializers.JSONField(default={})


class NotFoundResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    status_code = serializers.IntegerField(default=status.HTTP_404_NOT_FOUND)
    message = serializers.CharField(default=None, required=False)
    extra = serializers.JSONField(default={})


class UserRolePermissionDeniedSerializer(serializers.Serializer):
    detail = serializers.CharField(
        default="You do not have permission to perform this action.")
