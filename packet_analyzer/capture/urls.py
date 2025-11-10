# capture/urls.py
from django.urls import path
from . import views

app_name = 'capture'

urlpatterns = [
    # Example URL: /api/top-talkers/5/ for the last 5 minutes
    path('api/top-talkers/<str:minutes_str>/', views.get_top_talkers, name='top_talkers'),
    # Endpoint for checking network health
    path('api/health/check-ip/', views.check_ip_health, name='check_ip_health'),
    # Security alerts endpoint
    path('api/security-alerts/', views.get_security_alerts, name='get_security_alerts'),
]