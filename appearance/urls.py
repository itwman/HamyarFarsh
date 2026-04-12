from django.urls import path
from . import views

app_name = 'appearance'

urlpatterns = [
    path('', views.appearance_dashboard, name='dashboard'),

    # فهرست
    path('menu/create/', views.menu_create, name='menu_create'),
    path('menu/<int:pk>/edit/', views.menu_edit, name='menu_edit'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),

    # ویجت فوتر
    path('widget/create/', views.widget_create, name='widget_create'),
    path('widget/<int:pk>/edit/', views.widget_edit, name='widget_edit'),
    path('widget/<int:pk>/delete/', views.widget_delete, name='widget_delete'),

    # کد سفارشی و رنگ
    path('custom-code/', views.custom_code_settings, name='custom_code'),
]
