"""
API ساده برای محصولات و کاتالوگ
بدون نیاز به Django REST Framework
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from products.models import Product
from catalog_app.models import Catalog


@require_GET
def products_api(request):
    """لیست محصولات موجود (JSON)"""
    # فیلتر محصولات
    products = Product.objects.filter(
        status='available'
    ).select_related(
        'album__manufacturer',
        'background_color',
        'design_type'
    )[:50]
    
    # تبدیل به dict
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'manufacturer': p.album.manufacturer.name,
            'album': p.album.name,
            'comb': p.comb,
            'price_12m': int(p.get_sell_price_12m()),
            'color': p.background_color.name if p.background_color else None,
            'design': p.design_type.name if p.design_type else None,
            'url': f'/farsh/{p.slug}/',
        })
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'products': data
    })


@require_GET
def product_detail_api(request, slug):
    """جزئیات محصول (JSON)"""
    product = get_object_or_404(
        Product.objects.select_related(
            'album__manufacturer',
            'background_color',
            'design_type',
            'weave_type',
            'feature'
        ),
        slug=slug
    )
    
    # تصویر شاخص
    primary_image = product.primary_image
    image_url = None
    if primary_image and primary_image.featured_image:
        image_url = primary_image.featured_image.url
    
    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'manufacturer': product.album.manufacturer.name,
        'album': product.album.name,
        'comb': product.comb,
        'price_12m': int(product.get_sell_price_12m()),
        'color': product.background_color.name if product.background_color else None,
        'design': product.design_type.name if product.design_type else None,
        'weave': product.weave_type.name if product.weave_type else None,
        'feature': product.feature.name if product.feature else None,
        'status': product.status,
        'image': image_url,
        'url': f'/farsh/{product.slug}/',
    }
    
    return JsonResponse({
        'success': True,
        'product': data
    })


@require_GET
def catalog_api(request, code):
    """محصولات کاتالوگ (JSON)"""
    catalog = get_object_or_404(Catalog, unique_code=code)
    
    # بررسی انقضا
    if catalog.is_expired():
        return JsonResponse({
            'success': False,
            'error': 'Catalog expired'
        }, status=410)
    
    # محصولات
    products = catalog.products.filter(
        status='available'
    ).select_related('album__manufacturer')
    
    products_data = []
    for p in products:
        products_data.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'manufacturer': p.album.manufacturer.name,
            'price_12m': int(p.get_sell_price_12m()),
            'url': f'/farsh/{p.slug}/',
        })
    
    data = {
        'catalog': {
            'title': catalog.title,
            'code': catalog.unique_code,
            'created_at': catalog.created_at.isoformat(),
            'view_count': catalog.view_count,
            'expires_at': catalog.expires_at.isoformat() if catalog.expires_at else None,
        },
        'products': products_data,
        'count': len(products_data),
    }
    
    return JsonResponse({
        'success': True,
        **data
    })


@require_GET
def search_api(request):
    """جستجوی محصولات (JSON)"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Query too short'
        }, status=400)
    
    # جستجو
    products = Product.objects.filter(
        name__icontains=query,
        status='available'
    ).select_related('album__manufacturer')[:20]
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'manufacturer': p.album.manufacturer.name,
            'price_12m': int(p.get_sell_price_12m()),
            'url': f'/farsh/{p.slug}/',
        })
    
    return JsonResponse({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })
