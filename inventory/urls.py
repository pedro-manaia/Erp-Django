from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = "inventory"
urlpatterns = [
    path("", views.InventoryHomeView.as_view(), name="home"),

    # Cadastro placeholder
    path("cadastro/", TemplateView.as_view(template_name="portal/under_construction_inventory.html"), name="cadastro"),
    path("entradas/", views.EntryListView.as_view(), name="entries"),
    path("entradas/nova/", views.EntryCreateView.as_view(), name="entry_new"),
    path("correcao/", views.AdjustView.as_view(), name="adjust"),
    path("produtos/", include(("products.urls","products"), namespace="products")),
]
