from core import views
from django.urls import path

app_name = "core"

urlpatterns = [
    path('oauth2callback', views.get_google_token, name='get_google_token'),
    path('slide', views.test_google_api, name='test_google_api'),
    path('auth', views.google_auth, name='google_auth'),
]
