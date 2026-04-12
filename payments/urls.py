from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # ==================== فاز 8.1: پرداخت آنلاین ====================
    # درخواست پرداخت
    path('request/<int:order_id>/', views.payment_request, name='request'),
    
    # Callback درگاه
    path('callback/', views.payment_callback, name='callback'),
    
    # تأیید پرداخت
    path('verify/<str:tracking_code>/', views.payment_verify, name='verify'),
    
    # صفحه موفقیت/خطا
    path('success/<str:tracking_code>/', views.payment_success, name='success'),
    path('failed/<str:tracking_code>/', views.payment_failed, name='failed'),
    
    # ==================== فاز 8.2: سیستم اقساطی ====================
    # محاسبه‌گر اقساط
    path('calculator/', views.installment_calculator_view, name='calculator'),
    path('calculator/ajax/', views.installment_calculator_ajax, name='calculator_ajax'),
    
    # مدیریت اقساط
    path('installment/create/<int:order_id>/', views.create_installment_plan, name='create_installment'),
    path('installment/<int:plan_id>/', views.installment_plan_detail, name='installment_detail'),
    path('installment/<int:plan_id>/confirm/', views.confirm_installment_plan, name='confirm_installment'),
    
    # ==================== فاز 8.3: فاکتور و قیمت روز ====================
    # فاکتور
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice'),
    path('invoice/<int:order_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoice/<int:order_id>/update-prices/', views.apply_current_prices, name='apply_current_prices'),
]
