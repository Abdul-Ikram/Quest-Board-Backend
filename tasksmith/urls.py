from django.urls import path
from . import views

urlpatterns = [
    path('health-check/', views.HealthCheckView.as_view(), name='health_check')
]