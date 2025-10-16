from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce, Cast
from inventory.models import StockMovement
from sales.models import SalesOrderItem

# Campo decimal padrão para coerção/aggregates
DECIMAL = DecimalField(max_digits=20, decimal_places=2)
ZERO = Value(Decimal('0'), output_field=DECIMAL)

def _to_decimal(value):
    if value is None:
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')

def _sum_decimal(qs, field_name: str):
    # Garante tipos compatíveis no banco (evita FieldError: mixed types)
    return qs.aggregate(
        total=Coalesce(Sum(Cast(field_name, DECIMAL)), ZERO)
    )['total'] or Decimal('0')

def recompute_product_stock(product):
    """Recalcula o estoque_atual de um produto.
    Regra:
      estoque = entradas(IN) + ajustes(ADJ) - saidas(itens de pedidos confirmed/invoiced)
    """
    entradas_qs = StockMovement.objects.filter(produto=product, tipo='IN')
    ajustes_qs = StockMovement.objects.filter(produto=product, tipo='ADJ')
    saidas_qs = SalesOrderItem.objects.filter(
        produto=product,
        pedido__status__in=['confirmed', 'invoiced'],
    )

    total_in = _sum_decimal(entradas_qs, 'quantidade') + _sum_decimal(ajustes_qs, 'quantidade')
    total_out = _sum_decimal(saidas_qs, 'quantidade')

    novo = _to_decimal(total_in) - _to_decimal(total_out)

    # Atualiza somente se mudou
    if getattr(product, 'estoque_atual', None) != novo:
        product.estoque_atual = novo
        update_fields = ['estoque_atual']
        if hasattr(product, 'atualizado_em'):
            update_fields.append('atualizado_em')
        product.save(update_fields=update_fields)

    return product.estoque_atual

@transaction.atomic
def rebuild_all_products():
    from products.models import Product
    for p in Product.objects.select_for_update().all():
        recompute_product_stock(p)
