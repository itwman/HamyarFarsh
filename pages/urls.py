"""
فاز 14: URL های CMS
- پنل مدیریت: /cms/pages/ و /cms/categories/
- نمایش عمومی: /page/{slug}/ و /blog/
"""
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # ===== پنل مدیریت =====
    path('cms/pages/', views.page_list, name='page_list'),
    path('cms/pages/create/', views.page_create, name='page_create'),
    path('cms/pages/<int:pk>/edit/', views.page_edit, name='page_edit'),
    path('cms/pages/<int:pk>/delete/', views.page_delete, name='page_delete'),
    path('cms/pages/<int:pk>/toggle/', views.page_toggle_status, name='page_toggle_status'),

    # دسته‌بندی مقالات
    path('cms/categories/', views.category_list, name='category_list'),
    path('cms/categories/create/', views.category_create, name='category_create'),
    path('cms/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('cms/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # آپلود تصویر از ویرایشگر
    path('cms/upload-image/', views.editor_upload_image, name='editor_upload_image'),

    # ===== نمایش عمومی =====
    # بلاگ
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/category/<slug:slug>/', views.blog_by_category, name='blog_by_category'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # صفحات ایستا (آخرین ردیف — catch-all)
    path('page/<slug:slug>/', views.page_view, name='page_view'),
]
