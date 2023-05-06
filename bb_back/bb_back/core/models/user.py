from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, first_name, last_name,
                     **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password is not provided")

        user = self.model(email=self.normalize_email(email),
                          first_name=first_name,
                          last_name=last_name,
                          **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name,
                    **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, first_name, last_name,
                                 **extra_fields)

    def create_superuser(self, email, password, first_name, last_name,
                         **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, first_name, last_name,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=63, unique=True)
    login = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    team = models.ForeignKey("Team",
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="users")

    created_at = models.DateTimeField(default=timezone.now)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_email_confirmed = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "login", "password"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
