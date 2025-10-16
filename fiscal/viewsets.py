from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FiscalDocument
from .serializers import FiscalDocumentSerializer
from .services.provider import send_document

class FiscalDocumentViewSet(viewsets.ModelViewSet):
    queryset = FiscalDocument.objects.all().order_by("-criado_em")
    serializer_class = FiscalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def emitir(self, request):
        payload = request.data
        result = send_document(payload)
        doc = FiscalDocument.objects.create(
            tipo=payload.get("tipo","nfe"),
            json_envio=payload,
            situacao=result.get("status","em_processamento"),
            chave=result.get("chave",""),
            numero=result.get("numero"),
            serie=result.get("serie",1),
            xml=result.get("xml",""),
            provider_id=result.get("provider_id",""),
        )
        return Response(FiscalDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)
