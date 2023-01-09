from enum import IntEnum

# Emails
from typing import Dict


class EmailTypes(IntEnum):
    NONE_EMAIL = 0
    VERIFY_MAIL_ADDRESS_EMAIL = 1
    NEW_USER_GREETING_EMAIL = 2


EMAIL_TEMPLATE_NAMES: Dict[int, str] = {
    EmailTypes.NONE_EMAIL: "",
    EmailTypes.VERIFY_MAIL_ADDRESS_EMAIL: "verify_email_template",
    EmailTypes.NEW_USER_GREETING_EMAIL: "new_user_greeting_email_template"
}

EMAIL_SUBJECTS: Dict[int, str] = {
    EmailTypes.NONE_EMAIL: "",
    EmailTypes.VERIFY_MAIL_ADDRESS_EMAIL:
    "Битва Банков. Подтверждение почтового адреса.",
    EmailTypes.NEW_USER_GREETING_EMAIL: "Битва Банков. Успешная регистрация."
}
