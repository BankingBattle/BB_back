from typing import Dict, List
import os

from django.core.mail import EmailMultiAlternatives
from .utils import is_valid_email, uid_hex
from bb_back.core.constants import EMAIL_TEMPLATE_NAMES, EMAIL_SUBJECTS

from bb_back import settings
from bb_back.core.models import EmailLog, User, EmailVerificationCode


class EmailSender:
    TEMP_CONSTANT_LINK = "https://bankingbattle.ru"

    def __init__(self, to_users_emails: List[str], email_type: int):
        self._email_templates_path = os.path.join(settings.BASE_DIR,
                                                  settings.CORE_TEMPLATES_PATH,
                                                  'emails')
        self._from_email = settings.EMAIL_HOST_USER
        self._email_subject = EMAIL_SUBJECTS.get(email_type, "")
        self._email_template_name = EMAIL_TEMPLATE_NAMES.get(email_type)
        self._to_users_emails = [
            email for email in to_users_emails if is_valid_email(email)
        ]
        self._email_type = email_type

    def send_email(self, context: Dict[str, str]) -> None:
        email_template = self._get_email_template()
        email_content = email_template.format(**context)
        msg = EmailMultiAlternatives(subject=self._email_subject,
                                     from_email=self._from_email,
                                     to=self._to_users_emails)
        msg.attach_alternative(email_content, "text/html")
        msg.send()
        self._log_email()

    def _get_email_template(self) -> str:
        html_path = os.path.join(self._email_templates_path,
                                 f"{self._email_template_name}.html")
        with open(html_path, "r+") as f:
            template = f.read()
        return template

    def _log_email(self) -> None:
        EmailLog.objects.create(email_type=self._email_type,
                                receiver_email=", ".join(
                                    self._to_users_emails))

    @classmethod
    def get_mail_verification_link(cls, user: User) -> str:
        verification_code = uid_hex()
        EmailVerificationCode.objects.create(user=user, code=verification_code)
        link = f"{cls.TEMP_CONSTANT_LINK}"
        return link
