from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from customers.viewsets import CustomerViewSet
from products.viewsets import ProductViewSet
from sales.viewsets import SalesOrderViewSet, SalesOrderItemViewSet
from rental.viewsets import ReservationViewSet
from finance.viewsets import LedgerEntryViewSet
from fiscal.viewsets import FiscalDocumentViewSet
from scheduling.viewsets import EventViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"products", ProductViewSet)
router.register(r"sales-orders", SalesOrderViewSet)
router.register(r"sales-order-items", SalesOrderItemViewSet)
router.register(r"reservations", ReservationViewSet)
router.register(r"ledger", LedgerEntryViewSet)
router.register(r"fiscal-docs", FiscalDocumentViewSet)
router.register(r"events", EventViewSet)


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path('healthz', healthz, name='healthz'),
    path("", include("portal.urls")),
    path("admin/", admin.site.urls),
    path("financeiro/", include(("finance.urls","finance"), namespace="finance")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls")),
    path('config/dispositivos-ativos/', include('core.active_devices.urls')),
    path('notifications/', include('core.broadcast.urls')),
]
