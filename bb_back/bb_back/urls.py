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
from django.urls import path
from bb_back.settings import API_PREFIX, API_VERSION
from bb_back.core import views
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{API_PREFIX}/{API_VERSION}/register',
         views.RegistrationUserView.as_view()),
    path(f'{API_PREFIX}/{API_VERSION}/token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path(f'{API_PREFIX}/{API_VERSION}/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path(f'{API_PREFIX}/{API_VERSION}/token/verify/',
         TokenVerifyView.as_view(),
         name='token_verify'),
]
