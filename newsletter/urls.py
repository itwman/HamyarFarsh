from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # فرم عضویت (AJAX)
    path('subscribe/', views.subscribe_ajax, name='subscribe'),
    path('unsubscribe/<str:phone>/', views.unsubscribe, name='unsubscribe'),

    # پنل مدیریت مشترکین
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/subscriber/<int:pk>/delete/', views.subscriber_delete, name='subscriber_delete'),
    path('admin/subscriber/<int:pk>/toggle/', views.subscriber_toggle, name='subscriber_toggle'),
    path('admin/bulk-add/', views.bulk_add, name='bulk_add'),
    path('admin/bulk-import/', views.bulk_import, name='bulk_import'),
    path('admin/export/', views.export_csv, name='export_csv'),

    # کمپین
    path('admin/campaigns/', views.campaign_list, name='campaign_list'),
    path('admin/campaign/create/', views.campaign_create, name='campaign_create'),
    path('admin/campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('admin/campaign/<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),
    path('admin/campaign/<int:pk>/send/', views.campaign_send, name='campaign_send'),
    path('admin/campaign/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
]
