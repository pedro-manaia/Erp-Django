from django.core.management.base import BaseCommand
from products.models import Product
from inventory.stock_service import recompute_product_stock

class Command(BaseCommand):
    help = "Recalcula estoque_atual de todos os produtos."

    def handle(self, *args, **options):
        total = 0
        for p in Product.objects.all():
            recompute_product_stock(p)
            total += 1
        self.stdout.write(self.style.SUCCESS(f"Estoque recalculado para {total} produtos."))
