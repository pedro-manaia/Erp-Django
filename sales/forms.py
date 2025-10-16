from django import forms
from django.forms import inlineformset_factory
from customers.models import Customer
from .models import Quote, QuoteItem

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["tipo","nome","razao_social","cpf_cnpj","email","telefone","whatsapp","data_nascimento","endereco","cidade","uf","cep","ativo"]
        widgets = {f: forms.TextInput(attrs={"class":"form-control"}) for f in ["nome","razao_social","cpf_cnpj","telefone","whatsapp","endereco","cidade","uf","cep"]}
        widgets.update({
            "tipo": forms.Select(attrs={"class":"form-select"}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),
            "data_nascimento": forms.DateInput(attrs={"class":"form-control", "type":"date"}),
            "ativo": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        })

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["cliente","validade","desconto_total","observacoes","status"]
        widgets = {
            "cliente": forms.Select(attrs={"class":"form-select"}),
            "validade": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "desconto_total": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "observacoes": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "status": forms.Select(attrs={"class":"form-select"}),
        }

class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ["produto","descricao","quantidade","preco_unitario"]
        widgets = {
            "produto": forms.Select(attrs={"class":"form-select"}),
            "descricao": forms.TextInput(attrs={"class":"form-control","placeholder":"Descrição livre (se não selecionar produto)"}),
            "quantidade": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "preco_unitario": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
        }

QuoteItemFormSet = inlineformset_factory(Quote, QuoteItem, form=QuoteItemForm, extra=1, can_delete=True)


class SalesOrderPaymentForm(forms.Form):
    MEIOS = [
        ("Pix","Pix"),
        ("Dinheiro","Dinheiro"),
        ("Cartão de Débito","Cartão de Débito"),
        ("Cartão de Crédito","Cartão de Crédito"),
        ("Boleto","Boleto"),
        ("Transferência","Transferência"),
        ("Outro","Outro"),
    ]
    meio_pagamento = forms.ChoiceField(choices=MEIOS, widget=forms.Select(attrs={"class":"form-select"}))
