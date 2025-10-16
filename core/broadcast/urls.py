from django.urls import path
from .views import poll, send_form, send_ok

urlpatterns = [
    path("poll", poll, name="broadcast_poll"),
    path("admin/send", send_form, name="broadcast_send"),
    path("admin/sent", send_ok, name="broadcast_send_ok"),
]
