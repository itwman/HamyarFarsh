from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # لیست و مدیریت
    path('', views.product_list, name='product_list'),
    path('add/', views.product_add, name='product_add'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),

    # آپلود موقت (AJAX) برای صفحه افزودن محصول
    path('temp-upload/', views.temp_upload, name='temp_upload'),
    path('temp-upload/<int:pk>/delete/', views.temp_upload_delete, name='temp_upload_delete'),
    path('temp-upload/<int:pk>/set-primary/', views.temp_upload_set_primary, name='temp_upload_set_primary'),
    
    # مدیریت تصاویر
    path('<int:pk>/images/', views.product_images, name='product_images'),
    path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    path('image/<int:pk>/set-primary/', views.image_set_primary, name='image_set_primary'),

    # مدیریت رسانه (تصاویر + ویدیو)
    path('<int:pk>/media/', views.product_media, name='product_media'),
    path('video/<int:pk>/delete/', views.video_delete, name='video_delete'),
    
    # قوانین سایز
    path('<int:pk>/size-rules/', views.product_size_rules, name='product_size_rules'),
    
    # بروزرسانی انبوه
    path('bulk-price-update/', views.bulk_price_update, name='bulk_price_update'),

    # عملیات گروهی روی محصولات (حذف، تغییر وضعیت، تغییر آلبوم و ...)
    path('bulk-action/', views.bulk_action, name='bulk_action'),
]
