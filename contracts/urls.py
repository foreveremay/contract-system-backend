from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# 主路由器
router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'contracts', views.ContractViewSet)
# 為 CostItem, Payment, Invoice 建立完整的 CRUD API
router.register(r'costs', views.CostItemViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'invoices', views.InvoiceViewSet)


# 巢狀路由器 (用於在合約詳情頁中新增成本、付款等)
contracts_router = routers.NestedSimpleRouter(router, r'contracts', lookup='contract')
contracts_router.register(r'costs', views.CostItemViewSet, basename='contract-costs')
contracts_router.register(r'payments', views.PaymentViewSet, basename='contract-payments')
contracts_router.register(r'invoices', views.InvoiceViewSet, basename='contract-invoices')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(contracts_router.urls)),
]