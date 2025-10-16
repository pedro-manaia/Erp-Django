from rest_framework import serializers
from .models import FiscalDocument

class FiscalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalDocument
        fields = "__all__"
