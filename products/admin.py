from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id","sku","nome","preco_venda","estoque_atual","disponivel_para_locacao","ativo")
    search_fields = ("sku","nome","ncm")
    list_filter = ("ativo","disponivel_para_locacao")
