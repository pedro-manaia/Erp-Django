# core/active_devices/middleware.py
import time
from django.core.cache import cache

ACTIVE_KEY = "active_devices_map"      # dict {session_key: {...}}
TTL_SECONDS = 120                      # se o usuário ficar 2 min sem req, some da lista
STORE_TTL = 300                        # TTL do dicionário no cache

def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"

def _device_name(ua: str) -> str:
    ua = (ua or "").lower()
    if "android" in ua: return "Android"
    if "iphone" in ua or "ios" in ua: return "iPhone/iOS"
    if "ipad" in ua: return "iPad"
    if "windows" in ua: return "Windows"
    if "mac os x" in ua or "macintosh" in ua: return "macOS"
    if "linux" in ua: return "Linux"
    return "Dispositivo"

class ActiveDevicesMiddleware:
    """
    Marca presença de usuários autenticados no cache (volátil):
    - chave por session_key
    - dados: user, ip, user-agent, device, last_seen
    Some automaticamente após TTL_SECONDS sem atividade.
    Também mantém uma lista (volátil) de 'logins do dia' (primeiro visto).
    """
    TODAY_LOGINS_KEY = "today_logins"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            sess = getattr(request, "session", None)
            session_key = getattr(sess, "session_key", None)
            if session_key:
                ip = _client_ip(request)
                ua = request.META.get("HTTP_USER_AGENT", "")
                now = time.time()

                data = cache.get(ACTIVE_KEY) or {}
                # prune
                cutoff = now - TTL_SECONDS
                if data:
                    data = {k: v for k, v in data.items() if v.get("last_seen", 0) >= cutoff}

                first_time_seen = session_key not in data
                data[session_key] = {
                    "user_id": user.id,
                    "username": user.get_username(),
                    "ip": ip,
                    "user_agent": ua,
                    "device": _device_name(ua),
                    "last_seen": now,
                }
                cache.set(ACTIVE_KEY, data, timeout=STORE_TTL)

                # logins do dia (se primeira vez vista nessa sessão)
                if first_time_seen:
                    import datetime as dt
                    today_key = self.TODAY_LOGINS_KEY
                    payload = cache.get(today_key) or {"date": dt.date.today().isoformat(), "items": []}
                    if payload.get("date") != dt.date.today().isoformat():
                        payload = {"date": dt.date.today().isoformat(), "items": []}
                    payload["items"].insert(0, {
                        "ts": dt.datetime.now().strftime("%H:%M:%S"),
                        "date": dt.date.today().isoformat(),
                        "username": user.get_username(),
                        "ip": ip,
                        "user_agent": ua,
                    })
                    payload["items"] = payload["items"][:200]
                    cache.set(today_key, payload, timeout=60*60*24)

        return response