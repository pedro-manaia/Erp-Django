from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Q

from .models import Reservation
from .serializers import ReservationSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("produto","cliente").all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status","produto","cliente","inicio","fim"]
    search_fields = ["produto__nome","cliente__nome"]
    ordering_fields = ["inicio","fim","criado_em"]

    def create(self, request, *args, **kwargs):
        # Verifica disponibilidade simples (soma quantidades no período)
        data = request.data
        produto_id = data.get("produto")
        inicio = data.get("inicio")
        fim = data.get("fim")
        quantidade = int(data.get("quantidade", 1))

        if not all([produto_id, inicio, fim]):
            return Response({"detail": "produto, inicio e fim são obrigatórios."}, status=400)

        # Conflitos de intervalo
        qs = Reservation.objects.filter(
            produto_id=produto_id,
            status__in=["reserved","pickedup"]
        ).filter(
            Q(inicio__lte=fim) & Q(fim__gte=inicio)
        )
        reservadas = qs.aggregate(total=Sum("quantidade"))["total"] or 0

        # Estoque atual
        from products.models import Product
        produto = Product.objects.get(id=produto_id)
        disponivel = (produto.estoque_atual - reservadas) >= quantidade

        if not disponivel:
            return Response({"detail": "Quantidade indisponível para o período."}, status=400)

        return super().create(request, *args, **kwargs)
