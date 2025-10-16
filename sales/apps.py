from django.apps import AppConfig

class SalesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales"

    def ready(self):
        # Garante o registro dos signals
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
