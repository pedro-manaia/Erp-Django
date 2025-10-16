from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Announcement

CACHE_KEY = "global_announcement"

@receiver(post_save, sender=Announcement)
def on_save(sender, instance, created, **kwargs):
    if instance.active:
        cache.set(CACHE_KEY, {
            "message": instance.message,
            "level": instance.level,
            "expires_at": instance.expires_at.isoformat() if instance.expires_at else None,
        }, timeout=24*3600)

@receiver(post_delete, sender=Announcement)
def on_delete(sender, instance, **kwargs):
    cache.delete(CACHE_KEY)
