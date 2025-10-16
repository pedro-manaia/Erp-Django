from rest_framework import serializers
from .models import SalesOrder, SalesOrderItem

class SalesOrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = SalesOrderItem
        fields = ["id","pedido","produto","quantidade","preco_unitario","subtotal"]

class SalesOrderSerializer(serializers.ModelSerializer):
    itens = SalesOrderItemSerializer(many=True, read_only=True)
    total_bruto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_liquido = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrder
        fields = "__all__"
