# capture/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Example URL: /api/top-talkers/5/ for the last 5 minutes
    path('api/top-talkers/<str:minutes_str>/', views.get_top_talkers, name='top_talkers'),
]