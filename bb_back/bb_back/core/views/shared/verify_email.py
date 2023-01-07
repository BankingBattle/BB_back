from django.utils import timezone
from rest_framework.views import APIView

from bb_back.core.models import EmailVerificationCode
from bb_back.core.utils.view_utils import failed_validation_response, response


class VerifyEmailView(APIView):

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
        return response(data={})
