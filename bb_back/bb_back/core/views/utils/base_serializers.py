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
