from core import views
from django.urls import path

app_name = "core"

urlpatterns = [
    path('oauth2callback', views.get_google_token, name='get_google_token'),
]
