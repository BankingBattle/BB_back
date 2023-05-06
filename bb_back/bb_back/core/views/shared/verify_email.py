from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from bb_back.core.models import EmailVerificationCode
from bb_back.core.utils.view_utils import failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class VerifyEmailResponseSerializer(BaseResponseSerializer):
    response_data = serializers.JSONField(required=False)


class VerifyEmailView(APIView):
    order_by = openapi.Parameter('code',
                                 openapi.IN_QUERY,
                                 description="Email verification code",
                                 type=openapi.TYPE_STRING,
                                 maxLength=32)

    @swagger_auto_schema(
        manual_parameters=[order_by],
        responses={status.HTTP_200_OK: VerifyEmailResponseSerializer})
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return failed_validation_response(
                error="code: verification code was not provided")
        if len(code) > 32:
            return failed_validation_response(
                error=f"code: length {len(code)} > 32.")
        verification_code = EmailVerificationCode.objects.filter(
            code=code).order_by('-expires_at').first()
        if not verification_code:
            return failed_validation_response(
                error="Provided unknown verification code.")
        if timezone.now() >= verification_code.expires_at:
            return failed_validation_response(
                error=
                "Verification link already expired. Please request new one.")
        verification_code.user.is_email_confirmed = True
        verification_code.user.save()
        response_data = VerifyEmailResponseSerializer(response_data={})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
