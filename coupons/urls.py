from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    # API اعمال/حذف کوپن (AJAX از سبد خرید)
    path('apply/', views.apply_coupon, name='apply'),
    path('remove/', views.remove_coupon, name='remove'),

    # پنل مدیریت
    path('', views.coupon_list, name='coupon_list'),
    path('create/', views.coupon_create, name='coupon_create'),
    path('<int:pk>/edit/', views.coupon_edit, name='coupon_edit'),
    path('<int:pk>/delete/', views.coupon_delete, name='coupon_delete'),
    path('<int:pk>/toggle/', views.coupon_toggle, name='coupon_toggle'),
    path('<int:pk>/report/', views.coupon_report, name='coupon_report'),
    path('generate-code/', views.coupon_generate_code, name='generate_code'),
]
