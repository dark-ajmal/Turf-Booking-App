"""
URL configuration for TurfProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from TurfApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login_view'),
    path('signup/', views.signup_view, name='signup_view'),
    path('', views.landing_view, name='landing_view'),
    path('ownerdashboard/', views.owner_view, name='owner_view'),
    path('home/', views.home_view, name='home_view'),
    path('ownerlogin/', views.ownerlogin_view, name='ownerlogin_view'),
    path('cricket/', views.cricket_view, name='cricket_view'),
    path('football/',views.football_view, name='football_view'),
    path('badminton/', views.badminton_view, name='badminton_view'),
    path('turf/', views.turf_view, name='turf_view'),
]
