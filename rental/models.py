from django.db import models
from products.models import Product
from customers.models import Customer

class Reservation(models.Model):
    STATUS = (
        ("reserved","Reservado"),
        ("pickedup","Retirado/Em curso"),
        ("returned","Devolvido"),
        ("canceled","Cancelado"),
    )
    produto = models.ForeignKey(Product, on_delete=models.PROTECT, limit_choices_to={"disponivel_para_locacao": True})
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    inicio = models.DateField()
    fim = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default="reserved")
    valor_diaria = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    caucao = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.produto} ({self.inicio} a {self.fim}) x{self.quantidade} - {self.cliente}"
