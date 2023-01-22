from .registration import RegistrationUserView
from .token import (
    DecoratedTokenRefreshView,
    DecoratedTokenVerifyView,
    DecoratedTokenObtainPairView,
)
from .user import UserView
from .verify_email import VerifyEmailView
from .game import CreateGameView, GetGameView
from .submit_upload import SubmitView

__all__ = [
    "RegistrationUserView",
    "DecoratedTokenRefreshView",
    "DecoratedTokenVerifyView",
    "DecoratedTokenObtainPairView",
    "UserView",
    "VerifyEmailView",
    "CreateGameView",
    "GetGameView",
    "SubmitView",
]
