from django import forms
from .models import Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nome','sku','unidade','preco_venda','custo','ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class':'form-control'}),
            'sku': forms.TextInput(attrs={'class':'form-control'}),
            'unidade': forms.TextInput(attrs={'class':'form-control'}),
            'preco_venda': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'custo': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
