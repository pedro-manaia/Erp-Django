from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView, TemplateView
from . import views
from .views_extras import FinanceView, FiscalView, StaffView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="portal/login.html"), name="login"),
    path("logout/", views.logout_then_login, name="logout"),
    path("", views.HomeView.as_view(), name="home"),
    path("construcao/", TemplateView.as_view(template_name="portal/under_construction.html"), name="under_construction"),
    path("vendas/", include(("sales.urls", "sales"), namespace="sales")),
    path("vendas", RedirectView.as_view(pattern_name="sales:home", permanent=False), name="sales"),
    path("estoque/", include(("inventory.urls","inventory"), namespace="inventory")),
    path("estoque", RedirectView.as_view(pattern_name="inventory:home", permanent=False), name="inventory"),
    path("financeiro/", FinanceView.as_view(), name="finance"),
    path("financeiro/cadastro/", TemplateView.as_view(template_name="portal/finance_cadastro.html"), name="financeiro_cadastro"),
    path("fiscal/", FiscalView.as_view(), name="fiscal"),
    path("fiscal/cadastro/", TemplateView.as_view(template_name="portal/under_construction_fiscal.html"), name="fiscal_cadastro"),
    path("funcionario/cadastro/", TemplateView.as_view(template_name="portal/under_construction_staff.html"), name="staff_cadastro"),
    path("configuracao/", views.ConfigView.as_view(), name="config"),
    path("configuracao/cadastro/", TemplateView.as_view(template_name="portal/under_construction.html"), name="config_cadastro"),
    path("configuracao/usuarios/", views.ConfigUsersListView.as_view(), name="config_users"),
    path("configuracao/usuarios/novo/", views.ConfigUserCreateView.as_view(), name="config_user_new"),
    path("configuracao/usuarios/<int:pk>/editar/", views.ConfigUserEditView.as_view(), name="config_user_edit"),
    path("configuracao/usuarios/<int:pk>/senha/", views.ConfigUserPasswordView.as_view(), name="config_user_password"),
    path("funcionario/", StaffView.as_view(), name="staff"),
    path("configuracao/sistema/", views.ConfigSystemView.as_view(), name="config_system"),
]
