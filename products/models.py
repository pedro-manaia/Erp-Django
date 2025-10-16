# erp_plug_and_play/products/models.py
from django.db import models

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    preco_venda = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    custo = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # <-- ADICIONE ESTA LINHA
    # Fiscais (simples, ampliar depois)
    ncm = models.CharField(max_length=10, blank=True)
    cfop = models.CharField(max_length=10, blank=True)
    csosn = models.CharField(max_length=5, blank=True)
    cst_icms = models.CharField(max_length=5, blank=True)
    unidade = models.CharField(max_length=5, default="UN")

    # Estoque básico
    estoque_atual = models.IntegerField(default=0)

    # Locação
    disponivel_para_locacao = models.BooleanField(default=False)
    valor_diaria = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    caucao = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.nome}"
