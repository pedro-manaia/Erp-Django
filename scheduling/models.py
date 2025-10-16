from django.db import models
from customers.models import Customer

class Event(models.Model):
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    cliente = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    local = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.inicio} - {self.fim})"
