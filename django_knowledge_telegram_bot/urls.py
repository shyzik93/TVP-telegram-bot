from django.contrib import admin
from django.urls import path

from telegram.views import telegram_hook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/note/hook/telegram/<str:token>/', telegram_hook, name='api_telegram_hook'),
]
