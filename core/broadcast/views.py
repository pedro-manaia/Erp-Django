from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.utils import timezone

CACHE_KEY = "broadcast_current_toast"
DEFAULT_TTL = 60  # seconds

def _is_staff(u):
    return u.is_authenticated and u.is_staff

@login_required
@user_passes_test(_is_staff)
def send_form(request):
    if request.method == "POST":
        msg = (request.POST.get("message") or "").strip()
        level = (request.POST.get("level") or "info").strip()
        if level not in ("info","warn","alert"):
            return HttpResponseBadRequest("level inválido")
        if not msg:
            return HttpResponseBadRequest("mensagem vazia")
        cur = cache.get(CACHE_KEY) or {"id": 0}
        nid = int(timezone.now().timestamp() * 1000)
        payload = {"id": nid, "message": msg, "level": level, "ts": timezone.now().isoformat()}
        cache.set(CACHE_KEY, payload, timeout=DEFAULT_TTL)
        return redirect("broadcast_send_ok")
    return render(request, "admin/broadcast_send.html", {})

@login_required
@user_passes_test(_is_staff)
def send_ok(request):
    return render(request, "admin/broadcast_send_ok.html", {})

@login_required
def poll(request):
    # clients may pass last_id; if differs, return the latest toast
    try:
        last_id = int(request.GET.get("since_id") or 0)
    except ValueError:
        last_id = 0
    data = cache.get(CACHE_KEY)
    if not data:
        return JsonResponse({"has": False})
    # compute age from server send timestamp
    try:
        # data['ts'] is isoformat
        from datetime import datetime, timezone as _tz
        ts = datetime.fromisoformat(data.get("ts"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=_tz.utc)
        now = timezone.now()
        age_ms = int((now - ts).total_seconds() * 1000)
    except Exception:
        age_ms = 0
    # hard expire after 10s from SEND time
    DURATION_MS = 10000
    if age_ms >= DURATION_MS:
        cache.delete(CACHE_KEY)
        return JsonResponse({"has": False})
    # suppress if client already has this id
    if int(data.get("id", 0)) <= last_id:
        return JsonResponse({"has": False})
    # provide remaining time to clients
    remaining_ms = max(0, DURATION_MS - age_ms)
    payload = dict(data)
    payload["expires_in_ms"] = remaining_ms
    return JsonResponse({"has": True, "toast": payload})

    try:
        last_id = int(request.GET.get("since_id") or 0)
    except ValueError:
        last_id = 0
    data = cache.get(CACHE_KEY)
    if not data or int(data.get("id", 0)) <= last_id:
        return JsonResponse({"has": False})
    return JsonResponse({"has": True, "toast": data})
