from django.apps import AppConfig

class AnnouncementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.announcements"
    verbose_name = "Avisos/Broadcast"

    def ready(self):
        from . import signals  # noqa
