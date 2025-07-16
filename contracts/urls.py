from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'contracts', views.ContractViewSet, basename='contract')
router.register(r'categories', views.CategoryViewSet, basename='category') # 【新】註冊 Category API

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/contracts/<int:pk>/analysis/', views.contract_analysis_view, name='contract-analysis'),
]
