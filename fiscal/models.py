from django.db import models

class FiscalDocument(models.Model):
    TIPO = (("nfe","NF-e"),("nfce","NFC-e"),("nfse","NFS-e"))
    SITUACAO = (("em_processamento","Em processamento"),
                ("autorizada","Autorizada"),
                ("rejeitada","Rejeitada"))

    tipo = models.CharField(max_length=10, choices=TIPO)
    numero = models.IntegerField(null=True, blank=True)
    serie = models.IntegerField(default=1)
    chave = models.CharField(max_length=60, blank=True)
    situacao = models.CharField(max_length=20, choices=SITUACAO, default="em_processamento")
    xml = models.TextField(blank=True)
    json_envio = models.JSONField(default=dict)
    provider_id = models.CharField(max_length=100, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.serie}/{self.numero or '-'} - {self.situacao}"
