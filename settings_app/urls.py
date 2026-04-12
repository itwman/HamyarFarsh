from django.urls import path
from . import views

app_name = 'settings_app'  # اضافه شد - namespace

urlpatterns = [
    path('', views.settings_view, name='site_settings'),
]
