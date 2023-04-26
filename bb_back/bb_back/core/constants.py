from enum import IntEnum
from typing import Dict


# Emails
class EmailTypes(IntEnum):
    NONE_EMAIL = 0
    VERIFY_NEW_MAIL_ADDRESS_EMAIL = 1
    NEW_USER_GREETING_EMAIL = 2


EMAIL_TEMPLATE_NAMES: Dict[int, str] = {
    EmailTypes.NONE_EMAIL: "",
    EmailTypes.VERIFY_NEW_MAIL_ADDRESS_EMAIL: "verify_email_template",
    EmailTypes.NEW_USER_GREETING_EMAIL: "new_user_greeting_email_template"
}

EMAIL_SUBJECTS: Dict[int, str] = {
    EmailTypes.NONE_EMAIL: "",
    EmailTypes.VERIFY_NEW_MAIL_ADDRESS_EMAIL:
    "Битва Банков. Подтверждение почтового адреса.",
    EmailTypes.NEW_USER_GREETING_EMAIL: "Битва Банков. Успешная регистрация."
}


# Teams
class TeamApplicationStatusesEnum(IntEnum):
    STATUS_PENDING = 0
    STATUS_ACCEPTED = 1
    STATUS_REJECTED = 2


TEAM_APPLICATION_STATUSES_NAMES = {
    0: "STATUS_PENDING",
    1: "STATUS_ACCEPTED",
    2: "STATUS_REJECTED"
}

MEMBER_COUNT_LIMIT = 5
