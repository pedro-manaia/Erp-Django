from django.contrib import admin
from .models import SalesOrder, SalesOrderItem

class ItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("id","cliente","status","criado_por","criado_em")
    inlines = [ItemInline]
