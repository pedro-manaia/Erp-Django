from django import forms
from .models import StockMovement
from products.models import Product

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['produto','quantidade','custo_unitario','motivo']
        widgets = {
            'produto': forms.Select(attrs={'class':'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'custo_unitario': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'motivo': forms.TextInput(attrs={'class':'form-control'}),
        }
    def save(self, commit=True, user=None):
        obj = super().save(commit=False)
        obj.tipo = 'IN'
        if user and not obj.criado_por: obj.criado_por = user
        if commit: obj.save()
        return obj

class StockAdjustForm(forms.Form):
    produto = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    novo_estoque = forms.DecimalField(decimal_places=2, max_digits=12, widget=forms.NumberInput(attrs={'class':'form-control','step':'0.01'}))
    motivo = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Correção manual'}))
