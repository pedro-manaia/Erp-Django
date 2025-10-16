from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import LedgerEntry
from .serializers import LedgerEntrySerializer

class LedgerEntryViewSet(viewsets.ModelViewSet):
    queryset = LedgerEntry.objects.all().order_by("-created_at")
    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["tipo","cliente","vencimento","pago_em"]
    ordering_fields = ["vencimento","valor","created_at"]
