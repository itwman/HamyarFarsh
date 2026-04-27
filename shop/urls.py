from django.urls import path, re_path
from . import views

app_name = 'shop'

urlpatterns = [
    # کاتالوگ اصلی
    path('', views.catalog_view, name='catalog'),

    # امتیازدهی
    re_path(r'^(?P<slug>[\w\-]+)/rate/$', views.submit_rating, name='submit_rating'),

    # سفارش سایز خاص
    re_path(r'^(?P<slug>[\w\-]+)/custom-size/$', views.custom_size_request, name='custom_size_request'),

    # صفحه محصول — URL جدید با SKU: /farsh/IR1200-43025/slug/
    re_path(r'^(?P<sku>IR\d+-\d+)/(?P<slug>[\w\-]+)/$', views.product_detail_view, name='product_detail_sku'),

    # صفحه محصول — URL قدیمی (سازگاری): /farsh/slug/
    re_path(r'^(?P<slug>[\w\-]+)/$', views.product_detail_view, name='product_detail'),
]
