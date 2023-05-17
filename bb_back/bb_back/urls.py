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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from bb_back.core import views
from bb_back.core.views.internal.demo import DemoView
from bb_back.settings import API_PREFIX, API_VERSION, INTERNAL_API_PREFIX

schema_view = get_schema_view(
    openapi.Info(
        title="BB back swagger",
        default_version="v1.0.0",
        description="Banking Battle Backend",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
handler404 = views.view_404
urlpatterns = [
    path(f"{API_PREFIX}/{API_VERSION}/{INTERNAL_API_PREFIX}/healthcheck/app/",
         views.AppHealthCheckView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/{INTERNAL_API_PREFIX}/healthcheck/db/",
         views.DBHealthCheckView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/{INTERNAL_API_PREFIX}/demo/<int:status>/",
        DemoView.as_view()),
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}/{API_VERSION}/register/",
         views.RegistrationUserView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/user/me/", views.UserView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/",
        views.DecoratedTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/refresh/",
        views.DecoratedTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/token/verify/",
        views.DecoratedTokenVerifyView.as_view(),
        name="token_verify",
    ),
    re_path(
        f"{API_PREFIX}/{API_VERSION}/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        f"{API_PREFIX}/{API_VERSION}/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(f"{API_PREFIX}/{API_VERSION}/email/verify/",
         views.VerifyEmailView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/game/", views.CreateGameView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/game/<int:game_id>/",
         views.GameView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/game/logo/<int:game_id>/",
         views.GameLogoView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/submit/upload/",
        views.SubmitView.as_view(),
        name="files",
    ),
    path(f"{API_PREFIX}/{API_VERSION}/score/", views.ScoreView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/round/<int:round_id>/",
         views.RoundView.as_view()),
    path(f"{API_PREFIX}/{API_VERSION}/round/create/",
         views.CreateRoundView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/round/data/<int:round_id>/",
        views.GetRoundDataView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/round/uploud_data/<int:round_id>/",
        views.UploudRoundData.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/application/",
        views.TeamApplicationView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/application/review/",
        views.ReviewTeamApplicationView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/current/",
        views.CurrentTeamView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/",
        views.TeamListView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/member/<int:team_id>/",
        views.MemberApplicationView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/team/member/review/",
        views.ReviewMemberApplicationView.as_view(),
    ),
    path(
        f"{API_PREFIX}/{API_VERSION}/round/target/<int:round_id>/",
        views.UploadRoundTargetView.as_view(),
    ),
    re_path(r"^.*/$", views.view_404,
            name="error404"),  # regex for all endpoints. Has to be last.
]
