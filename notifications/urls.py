from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # API نوتیفیکیشن کاربر
    path('api/list/', views.notification_list_api, name='api_list'),
    path('api/mark-read/', views.notification_mark_read, name='mark_read'),
    path('api/mark-all-read/', views.notification_mark_all_read, name='mark_all_read'),
    path('all/', views.notification_page, name='page'),

    # dismiss اعلان
    path('dismiss/', views.announcement_dismiss, name='dismiss'),

    # پنل مدیریت
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # اعلان‌ها
    path('admin/announcement/create/', views.announcement_create, name='announcement_create'),
    path('admin/announcement/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('admin/announcement/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    # قالب پیامک
    path('admin/sms-template/create/', views.sms_template_create, name='sms_template_create'),
    path('admin/sms-template/<int:pk>/edit/', views.sms_template_edit, name='sms_template_edit'),
    path('admin/sms-template/<int:pk>/delete/', views.sms_template_delete, name='sms_template_delete'),

    # لاگ پیامک
    path('admin/sms-logs/', views.sms_log_list, name='sms_log_list'),
]
