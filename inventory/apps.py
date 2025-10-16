from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"
    verbose_name = "Estoque"

    def ready(self):
        # Garante o registro dos signals
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Nunca impedir o start da app se der erro de import
            pass
