from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("lancamento/<int:pk>/editar/", views.LedgerEntryEditView.as_view(), name="ledger_edit"),
    # Dashboard / Home
    path("", views.FinanceHomeView.as_view(), name="home"),
    # Cadastros / Config
    path("cadastro/", views.FinanceiroCadastroView.as_view(), name="cadastro"),
    path("accounts/", views.AccountsListCreateView.as_view(), name="accounts"),
    path("payment-methods/", views.PaymentMethodsView.as_view(), name="payment_methods"),
    # Listagens
    path("cr/", views.CRListView.as_view(), name="cr_list"),
    path("cp/", views.CPListView.as_view(), name="cp_list"),
    # Extrato
    path("cashbook/", views.CashbookView.as_view(), name="cashbook"),
    # Documento manual e baixa
    path("doc/new/", views.NewDocView.as_view(), name="new_doc"),
    path("doc/<int:pk>/baixa/", views.BaixaParcelaFormView.as_view(), name="baixa_parcela_form"),
    # Ações rápidas (POST dos cards da home)
    path("quick/cr/", views.QuickCRView.as_view(), name="quick_cr"),
    path("quick/cp/", views.QuickCPView.as_view(), name="quick_cp"),
    # Integrações com Vendas/Estoque (links GET)
    path("cr/from-order/<int:pk>/", views.CrFromOrderView.as_view(), name="cr_from_order"),
    path("cp/from-entry/<int:pk>/", views.GerarCPDeEntradaView.as_view(), name="cp_from_entry"),
    # Categorias (despesa/receita)
    path("categorias/despesa/", views.ExpenseCategoryListView.as_view(), name="expense_category_list"),
    path("categorias/despesa/nova/", views.ExpenseCategoryCreateView.as_view(), name="expense_category_new"),
    path("categorias/receita/", views.RevenueCategoryListView.as_view(), name="revenue_category_list"),
    path("categorias/receita/nova/", views.RevenueCategoryCreateView.as_view(), name="revenue_category_new"),
]
