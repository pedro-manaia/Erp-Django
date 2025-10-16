from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from customers.models import Customer

class FinanceDocument(models.Model):
    TIPO = (("CR","Conta a Receber"),("CP","Conta a Pagar"))
    STATUS = (("open","Em aberto"),("partial","Parcial"),("paid","Pago"),("canceled","Cancelado"))
    tipo = models.CharField(max_length=2, choices=TIPO)
    descricao = models.CharField(max_length=200)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    fornecedor_nome = models.CharField(max_length=150, blank=True)

    origem_ct = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    origem_id = models.PositiveIntegerField(null=True, blank=True)
    origem = GenericForeignKey("origem_ct", "origem_id")  # pode apontar para SalesOrder ou StockMovement

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} #{self.id} - {self.descricao} ({self.valor_total})"

    @property
    def total_em_parcelas(self):
        return sum((e.valor for e in self.lancamentos.all()), start=0)

    @property
    def quitado(self):
        # Considera quitado se todas as parcelas (lancamentos) têm pago_em preenchido
        qs = self.lancamentos.all()
        return qs.exists() and all(l.pago_em for l in qs)

class LedgerEntry(models.Model):
    TIPO = (("CR","Conta a Receber"),("CP","Conta a Pagar"))
    documento = models.ForeignKey(FinanceDocument, null=True, blank=True, related_name="lancamentos", on_delete=models.CASCADE)
    cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)
    tipo = models.CharField(max_length=2, choices=TIPO)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    vencimento = models.DateField()
    pago_em = models.DateField(null=True, blank=True)
    meio_pagamento = models.CharField(max_length=30, blank=True)  # Pix, Boleto, Cartão...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Classificação opcional (CP): categoria pai e categoria (filha)
    expense_category_parent = models.ForeignKey('ExpenseCategory', null=True, blank=True, related_name='+', on_delete=models.PROTECT)
    expense_category = models.ForeignKey('ExpenseCategory', null=True, blank=True, related_name='ledger_entries', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} ({self.valor})"

    @property
    def em_aberto(self):
        return self.pago_em is None


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=80)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Categoria de Despesa"
        verbose_name_plural = "Categorias de Despesa"
        unique_together = ('name','parent')

    def __str__(self):
        if self.parent:
            return f"{self.parent} / {self.name}"
        return self.name
