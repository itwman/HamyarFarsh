from django.urls import path
from . import views

app_name = 'catalog'  # اضافه شد - namespace

urlpatterns = [
    # شرکت‌ها (فاز 2)
    path('manufacturers/', views.manufacturer_list, name='manufacturer_list'),
    path('manufacturers/create/', views.manufacturer_create, name='manufacturer_create'),
    path('manufacturers/<int:pk>/edit/', views.manufacturer_edit, name='manufacturer_edit'),
    path('manufacturers/<int:pk>/delete/', views.manufacturer_delete, name='manufacturer_delete'),
    path('manufacturers/<int:pk>/toggle/', views.manufacturer_toggle, name='manufacturer_toggle'),
    # آلبوم‌ها (فاز 2)
    path('albums/', views.album_list, name='album_list'),
    path('albums/create/', views.album_create, name='album_create'),
    path('albums/<int:pk>/edit/', views.album_edit, name='album_edit'),
    path('albums/<int:pk>/delete/', views.album_delete, name='album_delete'),
    path('albums/<int:pk>/toggle/', views.album_toggle, name='album_toggle'),

    # === فاز 3: دسته‌بندی‌ها ===
    path('categories/', views.categories_dashboard, name='categories_dashboard'),

    # رنگ زمینه
    path('colors/', views.color_list, name='color_list'),
    path('colors/create/', views.color_create, name='color_create'),
    path('colors/<int:pk>/edit/', views.color_edit, name='color_edit'),
    path('colors/<int:pk>/delete/', views.color_delete, name='color_delete'),
    path('colors/<int:pk>/toggle/', views.color_toggle, name='color_toggle'),

    # نوع طرح
    path('designs/', views.design_list, name='design_list'),
    path('designs/create/', views.design_create, name='design_create'),
    path('designs/<int:pk>/edit/', views.design_edit, name='design_edit'),
    path('designs/<int:pk>/delete/', views.design_delete, name='design_delete'),
    path('designs/<int:pk>/toggle/', views.design_toggle, name='design_toggle'),

    # نوع بافت
    path('weaves/', views.weave_list, name='weave_list'),
    path('weaves/create/', views.weave_create, name='weave_create'),
    path('weaves/<int:pk>/edit/', views.weave_edit, name='weave_edit'),
    path('weaves/<int:pk>/delete/', views.weave_delete, name='weave_delete'),

    # ویژگی
    path('features/', views.feature_list, name='feature_list'),
    path('features/create/', views.feature_create, name='feature_create'),
    path('features/<int:pk>/edit/', views.feature_edit, name='feature_edit'),
    path('features/<int:pk>/delete/', views.feature_delete, name='feature_delete'),

    # تناژ رنگ
    path('tones/', views.tone_list, name='tone_list'),
    path('tones/create/', views.tone_create, name='tone_create'),
    path('tones/<int:pk>/edit/', views.tone_edit, name='tone_edit'),
    path('tones/<int:pk>/delete/', views.tone_delete, name='tone_delete'),

    # سایزهای فرش
    path('sizes/', views.size_list, name='size_list'),
    path('sizes/create/', views.size_create, name='size_create'),
    path('sizes/<int:pk>/edit/', views.size_edit, name='size_edit'),
    path('sizes/<int:pk>/delete/', views.size_delete, name='size_delete'),
    path('sizes/<int:pk>/toggle/', views.size_toggle, name='size_toggle'),
]
