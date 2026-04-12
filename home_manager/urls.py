from django.urls import path
from . import views

app_name = 'home_manager'

urlpatterns = [
    # داشبورد مدیریت صفحه اصلی
    path('', views.dashboard_home, name='dashboard'),

    # اسلایدر
    path('slider/create/', views.slider_create, name='slider_create'),
    path('slider/<int:pk>/edit/', views.slider_edit, name='slider_edit'),
    path('slider/<int:pk>/delete/', views.slider_delete, name='slider_delete'),

    # بنر
    path('banner/create/', views.banner_create, name='banner_create'),
    path('banner/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banner/<int:pk>/delete/', views.banner_delete, name='banner_delete'),

    # بخش سفارشی
    path('section/create/', views.section_create, name='section_create'),
    path('section/<int:pk>/edit/', views.section_edit, name='section_edit'),
    path('section/<int:pk>/delete/', views.section_delete, name='section_delete'),
]
