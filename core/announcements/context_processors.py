from django.core.cache import cache
from django.utils import timezone
from datetime import datetime
from .models import Announcement

CACHE_KEY = "global_announcement"

def global_announcement(request):
    data = cache.get(CACHE_KEY)
    # fallback: most recent active
    if not data:
        obj = Announcement.objects.filter(active=True).order_by("-created_at").first()
        if obj:
            data = {
                "message": obj.message,
                "level": obj.level,
                "expires_at": obj.expires_at.isoformat() if obj.expires_at else None,
            }
            cache.set(CACHE_KEY, data, 24*3600)
    # validate expiry
    if data and data.get("expires_at"):
        try:
            expires = datetime.fromisoformat(data["expires_at"])
            if timezone.now() > expires:
                cache.delete(CACHE_KEY)
                data = None
        except Exception:
            pass
    return {"GLOBAL_ANNOUNCEMENT": data}
