from datetime import datetime

from django.db import models
from django.utils import timezone

from bb_back.core.constants import EmailTypes


def get_email_verification_code_expiration_datetime() -> datetime:
    return timezone.now() + timezone.timedelta(days=365)


class EmailLog(models.Model):
    email_type = models.SmallIntegerField(null=False,
                                          default=EmailTypes.NONE_EMAIL)
    receiver_email = models.CharField(null=False, max_length=63)
    created_at = models.DateTimeField(default=timezone.now)


class EmailVerificationCode(models.Model):
    user = models.ForeignKey("User", null=False, on_delete=models.DO_NOTHING)
    code = models.CharField(max_length=32, null=False)
    expires_at = models.DateTimeField(
        default=get_email_verification_code_expiration_datetime)

    created_at = models.DateTimeField(default=timezone.now)
