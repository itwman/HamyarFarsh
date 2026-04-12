from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # لیست محصولات
    path('products/', views.products_api, name='products'),
    
    # جزئیات محصول
    path('product/<slug:slug>/', views.product_detail_api, name='product_detail'),
    
    # کاتالوگ
    path('catalog/<str:code>/', views.catalog_api, name='catalog'),
    
    # جستجو
    path('search/', views.search_api, name='search'),
]
