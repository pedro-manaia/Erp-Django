# core/active_devices/urls.py
from django.urls import path
from .views import active_devices_view

urlpatterns = [
    path("", active_devices_view, name="active_devices"),
]