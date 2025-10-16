from django.db import models
from django.conf import settings
from customers.models import Customer
from products.models import Product

class Quote(models.Model):  # Orçamento
    STATUS = (
        ("draft","Rascunho"),
        ("sent","Enviado"),
        ("approved","Aprovado"),
        ("rejected","Rejeitado"),
        ("canceled","Cancelado"),
        ("expired","Expirado"),
    )
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orcamentos")
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    validade = models.DateField(null=True, blank=True)
    desconto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    pedido = models.OneToOneField('SalesOrder', null=True, blank=True, on_delete=models.SET_NULL, related_name='orcamento_origem')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def total_bruto(self):
        return sum((i.subtotal for i in self.itens.all()), start=0)

    @property
    def total_liquido(self):
        return self.total_bruto - (self.desconto_total or 0)

    def __str__(self):
        return f"Orçamento #{self.id} - {self.cliente}"

class QuoteItem(models.Model):
    orcamento = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Product, null=True, blank=True, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200, blank=True)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return (self.quantidade or 0) * (self.preco_unitario or 0)

class SalesOrder(models.Model):  # Pedido
    STATUS = (
        ("draft","Rascunho"),
        ("confirmed","Confirmado"),
        ("invoiced","Faturado"),
        ("canceled","Cancelado"),
    )
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="pedidos")
    status = models.CharField(max_length=20, choices=STATUS, default="confirmed")
    desconto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def total_bruto(self):
        return sum((i.subtotal for i in self.itens.all()), start=0)

    @property
    def total_liquido(self):
        return self.total_bruto - (self.desconto_total or 0)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} ({self.status})"

class SalesOrderItem(models.Model):
    pedido = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Product, null=True, blank=True, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200, blank=True)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return (self.quantidade or 0) * (self.preco_unitario or 0)

# === Vendas: sinais embutidos (não requer apps.ready) ===
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

def _recalc(p):
    try:
        from inventory.stock_service import recompute_product_stock
        recompute_product_stock(p)
    except Exception:
        pass

@receiver([post_save, post_delete], sender=SalesOrderItem)
def _sales_item_changed(sender, instance, **kwargs):
    try:
        if instance and instance.produto_id:
            _recalc(instance.produto)
    except Exception:
        pass

@receiver(post_save, sender=SalesOrder)
def _sales_order_changed(sender, instance, **kwargs):
    # Ao salvar/mudar status do pedido, recalcula os produtos dos itens
    try:
        for it in instance.itens.all():
            if it.produto_id:
                _recalc(it.produto)
    except Exception:
        pass
# === Fim dos sinais embutidos ===
