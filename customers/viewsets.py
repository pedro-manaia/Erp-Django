from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer
from .serializers import CustomerSerializer
from core.permissions import IsStaffOrReadOnly

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-criado_em")
    serializer_class = CustomerSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["ativo", "tipo", "cidade", "uf"]
    search_fields = ["nome", "razao_social", "cpf_cnpj", "email"]
    ordering_fields = ["criado_em", "atualizado_em", "nome"]
