from django.contrib import admin
from django.urls import path

from multichat.views import (
    IndexView,
    discord_hook,
    telegram_hook,
)

urlpatterns = [
    path('api/v1/multichat/hook/telegram/<str:token>/', telegram_hook, name='api_multichat_telegram_hook'),
    path('api/v1/multichat/hook/discord/<str:token>/', discord_hook, name='api_multichat_discord_hook'),
    path('', IndexView.as_view(), name='multichat_index'),
]
