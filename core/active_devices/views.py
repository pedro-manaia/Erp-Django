# core/active_devices/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.core.cache import cache
from .middleware import ACTIVE_KEY, ActiveDevicesMiddleware
import time

def _is_config_user(u):
    return u.is_authenticated and u.is_staff

@login_required
@user_passes_test(_is_config_user)
def active_devices_view(request):
    now = time.time()
    data = cache.get(ACTIVE_KEY) or {}
    active_list = sorted(
        [
            {
                "username": v.get("username"),
                "ip": v.get("ip"),
                "device": v.get("device"),
                "user_agent": v.get("user_agent"),
                "last_seen_secs": int(now - v.get("last_seen", 0)),
            }
            for v in data.values()
        ],
        key=lambda x: (x["username"], x["ip"]),
    )

    logins = cache.get(ActiveDevicesMiddleware.TODAY_LOGINS_KEY) or {"date": "", "items": []}
    # NOTE: render to portal/active_devices.html to match your base template path
    return render(request, "portal/active_devices.html", {
        "active_list": active_list,
        "today_date": logins.get("date"),
        "today_logins": logins.get("items", []),
    })