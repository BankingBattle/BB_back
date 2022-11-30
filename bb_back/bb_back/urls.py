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

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f"{API_PREFIX}/{API_VERSION}/register",
         views.RegistrationUserView.as_view()),
    path(
        f"{API_PREFIX}/{API_VERSION}/auth",
        views.LoginUserView.as_view(),
    )
]
