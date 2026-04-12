from django.urls import path
from . import views

app_name = 'customer_panel'

urlpatterns = [
    # داشبورد
    path('', views.customer_dashboard, name='dashboard'),
    
    # سفارشات
    path('orders/', views.orders_history, name='orders_history'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    
    # آدرس‌ها
    path('addresses/', views.addresses_list, name='addresses_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.address_set_default, name='address_set_default'),
    
    # پروفایل
    path('profile/', views.profile_edit, name='profile_edit'),
]
