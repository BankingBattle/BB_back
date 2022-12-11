"""bb_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from bb_back.settings import API_PREFIX, API_VERSION
from bb_back.core import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="BB back swagger",
        default_version="v1.0.0",
        description="Banking Battle Backend",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}/{API_VERSION}/register", views.RegistrationUserView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),
    re_path(
        f"{API_PREFIX}/{API_VERSION}/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        f"{API_PREFIX}/{API_VERSION}redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/game/",
        views.GameView.as_view(),
        name="token_obtain_pair",
    ),
]
