from django.db import models
from django.conf import settings
from products.models import Product

class StockMovement(models.Model):
    MOV_TYPES = (('IN','Entrada'),('ADJ','Ajuste'))
    produto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movimentos')
    tipo = models.CharField(max_length=3, choices=MOV_TYPES)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    motivo = models.CharField(max_length=200, blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-criado_em']
    def __str__(self): return f"{self.get_tipo_display()} {self.quantidade} de {self.produto}"

# === Estoque: sinais embutidos (não requer apps.ready) ===
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

try:
    from .stock_service import recompute_product_stock
except Exception:  # fallback robusto
    def recompute_product_stock(product):  # pragma: no cover
        try:
            from inventory.stock_service import recompute_product_stock as _r
            return _r(product)
        except Exception:
            return getattr(product, "estoque_atual", 0)

@receiver([post_save, post_delete], sender=StockMovement)
def _inventory_movement_changed(sender, instance, **kwargs):
    # Sempre que houver entrada/ajuste, recalcula o estoque do produto
    try:
        if instance and instance.produto_id:
            recompute_product_stock(instance.produto)
    except Exception:
        # Nunca quebrar o fluxo do save
        pass
# === Fim dos sinais embutidos ===
