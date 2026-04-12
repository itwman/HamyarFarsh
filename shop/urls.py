from django.urls import path, re_path
from . import views

app_name = 'shop'

urlpatterns = [
    # کاتالوگ اصلی
    path('', views.catalog_view, name='catalog'),

    # امتیازدهی (قبل از slug عمومی)
    re_path(r'^(?P<slug>[\w\-]+)/rate/$', views.submit_rating, name='submit_rating'),

    # سفارش سایز خاص
    re_path(r'^(?P<slug>[\w\-]+)/custom-size/$', views.custom_size_request, name='custom_size_request'),

    # فیلتر بر اساس دسته‌بندی (SEO-friendly URLs) - این view ها هنوز ایجاد نشدن
    # re_path(r'^rang/(?P<slug>[\w\-]+)/$', views.catalog_by_color, name='by_color'),
    # re_path(r'^tarh/(?P<slug>[\w\-]+)/$', views.catalog_by_design, name='by_design'),
    # path('shaane/<int:comb>/', views.catalog_by_comb, name='by_comb'),
    # re_path(r'^brand/(?P<slug>[\w\-]+)/$', views.catalog_by_brand, name='by_brand'),

    # صفحه جزئیات محصول (آخرین pattern - Unicode slug)
    re_path(r'^(?P<slug>[\w\-]+)/$', views.product_detail_view, name='product_detail'),
]
