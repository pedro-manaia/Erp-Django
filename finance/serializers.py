from rest_framework import serializers
from django.utils import timezone
from .models import LedgerEntry

class LedgerEntrySerializer(serializers.ModelSerializer):
    status_dyn = serializers.SerializerMethodField()
    class Meta:
        model = LedgerEntry
        fields = "__all__"


    def get_status_dyn(self, obj):
        if getattr(obj, "pago_em", None):
            return "paid"
        today = timezone.localdate()
        if getattr(obj, "vencimento", None):
            if obj.vencimento == today:
                return "due_today"
            if obj.vencimento < today:
                return "overdue"
        return "open"
