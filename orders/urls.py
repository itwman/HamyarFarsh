"""
URL patterns برای اپ سفارشات
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # سبد خرید
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/add/', views.cart_add_ajax, name='cart_add_ajax'),  # ✅ اضافه شد
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    
    # تکمیل سفارش
    path('checkout/', views.checkout, name='checkout'),
    
    # سایز سفارشی
    path('custom-size/<int:product_id>/', views.custom_size_order, name='custom_size_order'),
    
    # سفارشات
    path('my-orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/payment/', views.order_payment, name='order_payment'),
    path('order/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
]
