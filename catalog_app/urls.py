from django.urls import path
from . import views

app_name = 'catalog_app'

urlpatterns = [
    # مشاهده کاتالوگ (عمومی)
    path('c/<str:code>/', views.catalog_view, name='view'),
    
    # مدیریت کاتالوگ (staff)
    path('create/', views.catalog_create, name='create'),
    path('success/<str:code>/', views.catalog_success, name='success'),
    path('list/', views.catalog_list, name='list'),
    path('delete/<int:pk>/', views.catalog_delete, name='delete'),
    
    # اشتراک محصول تکی
    path('share/<slug:slug>/', views.product_share, name='product_share'),
]
