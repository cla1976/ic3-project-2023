"""users_admin URL Configuration

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
from django.urls import path, include
from user_profile_api.views import video_feed, video, video_open_door, show_users, get_users, show_events, GetEventsView

urlpatterns = [
    #URLs de funcionalidades
    path('video/open_door/', video_open_door, name='video_open_door'),
    path('video/feed/', video_feed, name='video_feed'),
    path('show_users/get_users/', get_users, name='get_users'),
    path('show_events/get_events/', GetEventsView.as_view(), name='get_events'),

    #URLs de páginas para acceder
    path('video/', video, name='video'),
    path('show_users/', show_users, name='show_users'),
    path('show_events/', show_events, name='show_events'),
    path('', admin.site.urls),
]
