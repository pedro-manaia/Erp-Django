from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, View
from core.utils import has_module
from customers.models import Customer
from .models import Quote, QuoteItem, SalesOrder, SalesOrderItem
from .forms import CustomerForm, QuoteForm, QuoteItemFormSet

class VendasRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True
    def test_func(self):
        return has_module(self.request.user, "vendas")

class SalesHomeView(VendasRequiredMixin, TemplateView):
    template_name = "sales/home.html"

# ---- Clientes ----
class CustomerListView(VendasRequiredMixin, ListView):
    model = Customer
    template_name = "sales/customers_list.html"
    paginate_by = 25

    def get_queryset(self):
        qs = Customer.objects.all().order_by("nome")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(razao_social__icontains=q) | qs.filter(email__icontains=q) | qs.filter(cpf_cnpj__icontains=q)
        return qs

class CustomerCreateView(VendasRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customers")

class CustomerUpdateView(VendasRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customers")

# ---- Orçamentos ----
class QuoteListView(VendasRequiredMixin, ListView):
    model = Quote
    template_name = "sales/quotes_list.html"
    paginate_by = 25

    def get_queryset(self):
        qs = Quote.objects.select_related("cliente").all().order_by("-criado_em")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

class QuoteCreateView(VendasRequiredMixin, View):
    template_name = "sales/quote_form.html"

    def get(self, request):
        form = QuoteForm()
        formset = QuoteItemFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    @transaction.atomic
    def post(self, request):
        form = QuoteForm(request.POST)
        formset = QuoteItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            quote = form.save(commit=False)
            quote.criado_por = request.user
            quote.save()
            formset.instance = quote
            formset.save()
            messages.success(request, "Orçamento criado.")
            return redirect("sales:quote_detail", pk=quote.pk)
        return render(request, self.template_name, {"form": form, "formset": formset})

class QuoteUpdateView(VendasRequiredMixin, View):
    template_name = "sales/quote_form.html"

    def get(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        form = QuoteForm(instance=quote)
        formset = QuoteItemFormSet(instance=quote)
        return render(request, self.template_name, {"form": form, "formset": formset, "object": quote})

    @transaction.atomic
    def post(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        form = QuoteForm(request.POST, instance=quote)
        formset = QuoteItemFormSet(request.POST, instance=quote)
        if form.is_valid() and formset.is_valid():
            quote = form.save()
            formset.save()
            messages.success(request, "Orçamento atualizado.")
            return redirect("sales:quote_detail", pk=quote.pk)
        return render(request, self.template_name, {"form": form, "formset": formset, "object": quote})

class QuoteDetailView(VendasRequiredMixin, DetailView):
    model = Quote
    template_name = "sales/quote_detail.html"

class QuoteApproveView(VendasRequiredMixin, View):
    def post(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        if quote.status == "approved" and quote.pedido_id:
            messages.info(request, "Este orçamento já foi aprovado.")
            return redirect("sales:order_detail", pk=quote.pedido_id)
        with transaction.atomic():
            order = SalesOrder.objects.create(
                cliente=quote.cliente,
                desconto_total=quote.desconto_total,
                observacoes=f"Convertido do Orçamento #{quote.id}",
                criado_por=request.user,
                status="confirmed",
            )
            for item in quote.itens.all():
                SalesOrderItem.objects.create(
                    pedido=order,
                    produto=item.produto,
                    descricao=item.descricao,
                    quantidade=item.quantidade,
                    preco_unitario=item.preco_unitario,
                )
            quote.status = "approved"
            quote.pedido = order
            quote.save()
        messages.success(request, f"Orçamento aprovado e convertido em Pedido #{order.id}.")
        return redirect("sales:order_detail", pk=order.pk)

# ---- Pedidos ----
class SalesOrderListView(VendasRequiredMixin, ListView):
    model = SalesOrder
    template_name = "sales/orders_list.html"
    paginate_by = 25

    def get_queryset(self):
        return SalesOrder.objects.select_related("cliente").all().order_by("-criado_em")

class SalesOrderDetailView(VendasRequiredMixin, DetailView):
    model = SalesOrder
    template_name = "sales/order_detail.html"


class SalesOrderPaymentView(VendasRequiredMixin, View):
    def post(self, request, pk):
        from .models import SalesOrder
        from finance import services as fin
        from datetime import date
        order = get_object_or_404(SalesOrder, pk=pk)
        meio = request.POST.get("meio_pagamento","").strip()
        try:
            if not fin.has_document_for_origin("sales","SalesOrder", order.id, "CR"):
                fin.gerar_cr_de_pedido(order_id=order.id, parcelas=1, primeiro_vencimento=date.today(), intervalo_dias=30, meio_pagamento=meio)
                messages.success(request, "Contas a Receber gerado a partir do pedido.")
            else:
                messages.info(request, "Já existe um documento de CR para este pedido.")
        except Exception as e:
            messages.error(request, f"Falha ao gerar CR: {e}")
        return redirect("sales:order_detail", pk=order.id)
