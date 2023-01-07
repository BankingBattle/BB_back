import uuid
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def is_valid_email(email) -> bool:
    try:
        validate_email(email)
    except ValidationError:
        return False
    else:
        return True


def uid_hex() -> str:
    return uuid.uuid4().hex
