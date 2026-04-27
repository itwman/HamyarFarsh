"""URL configuration for hamyarfarsh project."""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve as static_serve
import os

from shop.views import search_view, live_search_api, product_detail_view


def sku_redirect(request, sku):
    """ریدایرکت /IR1200-43025/ به /IR1200-43025/slug/"""
    from django.shortcuts import get_object_or_404, redirect
    from products.models import Product
    product = get_object_or_404(Product, sku=sku.upper())
    return redirect(f'/{product.sku}/{product.slug}/', permanent=True)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('settings/', include('settings_app.urls')),
    path('catalog/', include('catalog.urls')),
    path('admin-products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),

    # سرچ
    path('search/', search_view, name='search'),
    path('search/live/', live_search_api, name='live_search'),

    # فروشگاه (کاتالوگ + URL قدیمی slug)
    path('farsh/', include('shop.urls')),

    # URL محصول با SKU: /IR1200-43025/slug/
    re_path(r'^(?P<sku>IR\d+-\d+)/(?P<slug>[\w\-]+)/$', product_detail_view, name='sku_product'),

    # ریدایرکت SKU کوتاه: /IR1200-43025/ -> /IR1200-43025/slug/
    re_path(r'^(?P<sku>IR\d+-\d+)/$', sku_redirect, name='sku_redirect'),

    # گالری
    path('gallery/', include('gallery.urls')),

    # CMS
    path('', include('pages.urls')),
    path('', include('accounts.urls_home')),

    # داشبورد
    path('dashboard/', include('dashboard.urls')),
    path('dashboard/home-manager/', include('home_manager.urls')),
    path('dashboard/appearance/', include('appearance.urls')),
    path('dashboard/coupons/', include('coupons.urls')),

    # ماژول‌ها
    path('wishlist/', include('wishlist.urls')),
    path('notifications/', include('notifications.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('chat/', include('live_chat.urls')),
    path('catalog/', include('catalog_app.urls')),
    path('api/', include('api.urls')),
    path('panel/', include('customer_panel.urls')),

    # PWA
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('sw.js', static_serve, {
        'path': 'sw.js',
        'document_root': os.path.join(settings.BASE_DIR, 'static'),
    }, name='service_worker'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
