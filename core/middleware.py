
import re
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth import logout
from core.models import SystemConfig

EXEMPT_URLS = [
    r"^/admin/.*$",
    r"^/login/.*$",
    r"^/accounts/login/.*$",
    r"^/logout/.*$",
    r"^/sair/.*$",
    r"^/healthz/?$",
    r"^/static/.*$",
    r"^/media/.*$",
    r"^/api/.*$",
]

class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        # bypass
        for pattern in EXEMPT_URLS:
            if re.match(pattern, path):
                return None

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            login_url = reverse("login")
            return redirect(f"{login_url}?next={path}")

        # Read config
        cfg = SystemConfig.get_solo()
        if cfg.session_expire_on_close:
            request.session.set_expiry(0)

        idle_minutes = int(cfg.idle_timeout_minutes or 0)
        if idle_minutes < 1:
            idle_minutes = 1
        now_ts = int(timezone.now().timestamp())
        last = request.session.get("last_activity_ts")
        if last and (now_ts - int(last)) > idle_minutes * 60:
            logout(request)
            login_url = reverse("login")
            return redirect(f"{login_url}?next={path}")
        request.session["last_activity_ts"] = now_ts
        return None

    def process_response(self, request, response):
        if getattr(request, "user", None) and getattr(request, "user").is_authenticated:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response
