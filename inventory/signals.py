from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from inventory.models import StockMovement
from inventory.stock_service import recompute_product_stock

@receiver([post_save, post_delete], sender=StockMovement)
def _inventory_movement_changed(sender, instance, **kwargs):
    # Sempre que houver uma entrada/ajuste, recalcule o estoque do produto
    try:
        if instance and instance.produto_id:
            recompute_product_stock(instance.produto)
    except Exception:
        # Não quebrar o fluxo do save
        pass
