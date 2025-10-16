from django.urls import path
from . import views
app_name = "products"
urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("novo/", views.ProductCreateView.as_view(), name="new"),
    path("<int:pk>/editar/", views.ProductUpdateView.as_view(), name="edit"),
]
