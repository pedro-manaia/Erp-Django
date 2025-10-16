from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from core.utils import has_module
from .models import Product
from .forms import ProductForm

class EstoqueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True
    def test_func(self): return has_module(self.request.user, "estoque")

class ProductListView(EstoqueRequiredMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    paginate_by = 25
    def get_queryset(self):
        qs = Product.objects.all().order_by("nome")
        q = self.request.GET.get("q")
        if q: qs = qs.filter(nome__icontains=q) | qs.filter(sku__icontains=q)
        return qs

class ProductCreateView(EstoqueRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("inventory:products:list")

class ProductUpdateView(EstoqueRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("inventory:products:list")
