from django.db import models
from django.contrib.auth import get_user_model

class Announcement(models.Model):
    INFO = "info"
    WARN = "warn"
    ALERT = "alert"
    LEVEL_CHOICES = [
        (INFO, "Informação (verde)"),
        (WARN, "Cuidado (amarelo)"),
        (ALERT, "Atenção (vermelho)"),
    ]
    message = models.TextField("Mensagem")
    level = models.CharField("Nível", max_length=10, choices=LEVEL_CHOICES, default=INFO)
    active = models.BooleanField("Ativo", default=True)
    expires_at = models.DateTimeField("Expira em", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"

    def __str__(self):
        return f"[{self.get_level_display()}] {self.message[:40]}"
