from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/password/', views.user_password_reset, name='user_password_reset'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
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

    # مدیریت فضای رسانه
    path('media-storage/', views.media_storage, name='media_storage'),

    # API نوتیفیکیشن زنده (polling)
    path('api/live-alerts/', views.live_alerts_api, name='live_alerts'),
]
