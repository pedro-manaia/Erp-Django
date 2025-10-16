from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from sales.models import SalesOrderItem, SalesOrder
from inventory.stock_service import recompute_product_stock

@receiver([post_save, post_delete], sender=SalesOrderItem)
def _sales_item_changed(sender, instance, **kwargs):
    # Itens de pedido afetam o estoque quando o pedido está confirmado/invoiced.
    try:
        if instance and instance.produto_id:
            recompute_product_stock(instance.produto)
    except Exception:
        pass

@receiver(post_save, sender=SalesOrder)
def _sales_order_changed(sender, instance, **kwargs):
    # Ao salvar o pedido (ex.: mudar status), recalcule os produtos do pedido
    try:
        from sales.models import SalesOrderItem
        for it in SalesOrderItem.objects.filter(pedido=instance).select_related("produto"):
            if it.produto_id:
                recompute_product_stock(it.produto)
    except Exception:
        pass
