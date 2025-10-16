from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "sales"

urlpatterns = [
    path("", views.SalesHomeView.as_view(), name="home"),

    # Cadastro placeholder
    path("cadastro/", TemplateView.as_view(template_name="portal/under_construction_sales.html"), name="cadastro"),

    # Clientes
    path("clientes/", views.CustomerListView.as_view(), name="customers"),
    path("clientes/novo/", views.CustomerCreateView.as_view(), name="customer_new"),
    path("clientes/<int:pk>/editar/", views.CustomerUpdateView.as_view(), name="customer_edit"),

    # Orçamentos
    path("orcamentos/", views.QuoteListView.as_view(), name="quotes"),
    path("orcamentos/novo/", views.QuoteCreateView.as_view(), name="quote_new"),
    path("orcamentos/<int:pk>/", views.QuoteDetailView.as_view(), name="quote_detail"),
    path("orcamentos/<int:pk>/editar/", views.QuoteUpdateView.as_view(), name="quote_edit"),
    path("orcamentos/<int:pk>/aprovar/", views.QuoteApproveView.as_view(), name="quote_approve"),

    # Pedidos
    path("pedidos/", views.SalesOrderListView.as_view(), name="orders"),
    path("pedidos/<int:pk>/", views.SalesOrderDetailView.as_view(), name="order_detail"),
    path("pedidos/<int:pk>/pagamento/", views.SalesOrderPaymentView.as_view(), name="order_payment"),
]
