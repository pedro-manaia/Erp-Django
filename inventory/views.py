from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from core.utils import has_module
from .models import StockMovement
from .forms import StockEntryForm, StockAdjustForm

class EstoqueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True
    def test_func(self): return has_module(self.request.user, "estoque")

class InventoryHomeView(EstoqueRequiredMixin, TemplateView):
    template_name = "inventory/home.html"

class EntryListView(EstoqueRequiredMixin, ListView):
    model = StockMovement
    template_name = "inventory/entries_list.html"
    paginate_by = 25
    def get_queryset(self):
        return StockMovement.objects.select_related('produto','criado_por').all()

class EntryCreateView(EstoqueRequiredMixin, CreateView):
    form_class = StockEntryForm
    template_name = "inventory/entry_form.html"
    success_url = reverse_lazy("inventory:entries")
    def form_valid(self, form):
        obj = form.save(user=self.request.user)
        # Gera CP automaticamente para a entrada
        try:
            from finance import services as fin
            from datetime import date
            fin.gerar_cp_de_entrada_estoque(mov_id=obj.id, parcelas=1, primeiro_vencimento=date.today(), intervalo_dias=30)
            messages.success(self.request, "Entrada registrada e CP gerado.")
        except Exception as e:
            messages.warning(self.request, f"Entrada registrada, mas não foi possível gerar CP automaticamente: {e}")
        return super().form_valid(form)

class AdjustView(EstoqueRequiredMixin, FormView):
    template_name = "inventory/adjust_form.html"
    form_class = StockAdjustForm
    success_url = reverse_lazy("inventory:home")
    def form_valid(self, form):
        produto = form.cleaned_data['produto']
        novo = form.cleaned_data['novo_estoque']
        motivo = form.cleaned_data.get('motivo') or "Ajuste de estoque"
        atual = produto.estoque_atual
        delta = Decimal(novo) - Decimal(atual)
        if delta == 0:
            messages.info(self.request, "Estoque já está no valor informado.")
            return super().form_valid(form)
        StockMovement.objects.create(produto=produto, tipo='ADJ', quantidade=delta, motivo=motivo, criado_por=self.request.user)
        messages.success(self.request, f"Ajuste aplicado. Delta: {delta}.")
        return super().form_valid(form)
