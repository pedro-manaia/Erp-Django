
from django.db import models

class SystemConfig(models.Model):
    id = models.SmallAutoField(primary_key=True)
    session_expire_on_close = models.BooleanField(
        default=True,
        verbose_name="Expirar sessão ao fechar o navegador"
    )
    idle_timeout_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Tempo de inatividade (minutos)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuração do Sistema"
