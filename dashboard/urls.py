from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('sms/', views.sms_settings, name='sms_settings'),
    path('sms/test/', views.sms_test_connection, name='sms_test'),  # ✅ تست اتصال
    path('reports/', views.reports, name='reports'),
    
    # مدیریت سفارشات
    path('orders/', views.orders_manage, name='orders_manage'),
    path('orders/<int:order_id>/', views.order_detail_admin, name='order_detail_admin'),

    # مدیریت نظرات
    path('reviews/', views.reviews_manage, name='reviews_manage'),
    path('reviews/<int:pk>/action/', views.review_action, name='review_action'),
    path('reviews/bulk/', views.reviews_bulk_action, name='reviews_bulk_action'),
]
