from django.views.generic import TemplateView
from .views import ModuleRequiredMixin

class SalesView(ModuleRequiredMixin, TemplateView):
    module = "vendas"
    template_name = "portal/module_sales.html"

class FinanceView(ModuleRequiredMixin, TemplateView):
    module = "financeiro"
    template_name = "portal/module_finance.html"

class FiscalView(ModuleRequiredMixin, TemplateView):
    module = "fiscal"
    template_name = "portal/module_fiscal.html"

class StaffView(ModuleRequiredMixin, TemplateView):
    module = "funcionario"
    template_name = "portal/module_staff.html"

class InventoryView(ModuleRequiredMixin, TemplateView):
    module = "estoque"
    template_name = "portal/module_inventory.html"
