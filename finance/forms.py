from django import forms
from django.utils import timezone
from .models import ExpenseCategory
from . import services

TIPO_CHOICES = (("CR","Conta a Receber"),("CP","Conta a Pagar"))


class ExpenseCategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if getattr(obj, 'parent', None):
            return f"{obj.parent.name}/{obj.name}"
        return obj.name


class GerarTituloForm(forms.Form):
    categoria = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.all(), required=True, label="Categoria")
    parcelas = forms.IntegerField(min_value=1, initial=1, label="Parcelas")
    primeiro_vencimento = forms.DateField(required=False, label="1º Vencimento")
    intervalo_dias = forms.IntegerField(min_value=1, initial=30, label="Intervalo (dias)")


class QuickCRForm(forms.Form):
    pedido_id = forms.IntegerField(min_value=1, label="Pedido #")
    parcelas = forms.IntegerField(min_value=1, initial=1, label="Parcelas")
    primeiro_vencimento = forms.DateField(required=False, label="1º Vencimento")
    intervalo_dias = forms.IntegerField(min_value=1, initial=30, label="Intervalo (dias)")
    categoria = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.all(), required=True, label="Categoria")


class QuickCPForm(forms.Form):
    entrada_id = forms.IntegerField(min_value=1, label="Entrada Estoque #")
    parcelas = forms.IntegerField(min_value=1, initial=1, label="Parcelas")
    primeiro_vencimento = forms.DateField(required=False, label="1º Vencimento")
    intervalo_dias = forms.IntegerField(min_value=1, initial=30, label="Intervalo (dias)")
    categoria = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.all(), required=True, label="Categoria")


def _account_choices():
    try:
        items = services.list_accounts()
        out = [('', '— selecione —')]
        for a in items:
            out.append((str(a.get('id')), a.get('nome','')))
        return out
    except Exception:
        return [('', '— selecione —')]


def _payment_choices():
    try:
        items = services.list_payment_methods()
        out = [('', '— selecione —')]
        for it in items:
            name = it.get('nome','')
            out.append((name, name))
        return out
    except Exception:
        return [('', '— selecione —')]


class BaixaForm(forms.Form):
    data_pagto = forms.DateField(initial=timezone.localdate, label="Data do pagamento")
    conta_id = forms.ChoiceField(choices=(), label="Conta (caixa/banco)")
    meio_pagamento = forms.ChoiceField(choices=(), required=False, label="Forma de Pagamento")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conta_id'].choices = _account_choices()
        self.fields['meio_pagamento'].choices = _payment_choices()


class NewDocForm(forms.Form):
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo")
    descricao = forms.CharField(label="Descrição")
    parceiro_nome = forms.CharField(required=False, label="Cliente/Fornecedor")
    valor_total = forms.DecimalField(decimal_places=2, max_digits=12, label="Valor total")
    parcelas = forms.IntegerField(min_value=1, initial=1, label="Parcelas")
    primeiro_vencimento = forms.DateField(required=False, label="1º Vencimento")
    intervalo_dias = forms.IntegerField(min_value=1, initial=30, label="Intervalo (dias)")
    categoria = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.all(), required=True, label="Categoria")


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "parent"]
        labels = {"name": "Nome", "parent": "Categoria-pai (opcional)"}        


def _root_name_of_category(cat):
    # retorna o nome do ancestral raiz (ou o próprio)
    while getattr(cat, "parent_id", None):
        cat = cat.parent
    return (cat.name or "").strip()


class LedgerEntryForm(forms.Form):
    descricao = forms.CharField(label="Descrição")
    valor = forms.DecimalField(decimal_places=2, max_digits=12, label="Valor")
    vencimento = forms.DateField(label="Vencimento")
    categoria = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.all(), required=True, label="Categoria")

