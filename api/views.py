"""
API ساده برای محصولات و کاتالوگ
بدون نیاز به Django REST Framework
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.core.paginator import Paginator

from products.models import Product
from catalog_app.models import Catalog
from shop.views import build_search_q


@require_GET
def products_api(request):
    """لیست محصولات موجود (JSON)"""
    products = Product.objects.filter(
        status='available'
    ).select_related(
        'album__manufacturer',
        'background_color',
    ).prefetch_related('design_type')[:50]

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
            'design': p.design_type_display,
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
            'weave_type',
            'feature'
        ).prefetch_related('design_type'),
        slug=slug
    )

    primary_image = product.primary_image
    image_url = None
    if primary_image:
        if primary_image.featured_image:
            image_url = primary_image.featured_image.url
        elif primary_image.thumbnail:
            image_url = primary_image.thumbnail.url

    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'manufacturer': product.album.manufacturer.name,
        'album': product.album.name,
        'comb': product.comb,
        'price_12m': int(product.get_sell_price_12m()),
        'color': product.background_color.name if product.background_color else None,
        'design': product.design_type_display,
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

    if catalog.is_expired():
        return JsonResponse({
            'success': False,
            'error': 'Catalog expired'
        }, status=410)

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
    """
    جستجوی پیشرفته محصولات (JSON)
    پارامترها:
        q: عبارت جستجو (حداقل ۲ کاراکتر)
        page: شماره صفحه (پیش‌فرض ۱)
        per_page: تعداد در هر صفحه (پیش‌فرض ۲۰)
        manufacturer: فیلتر شرکت (id)
        comb: فیلتر شانه
        color: فیلتر رنگ زمینه (id)
        design: فیلتر نوع طرح (id)
        weave: فیلتر نوع بافت (id)
        status: فیلتر وضعیت
        sort: مرتب‌سازی (newest/oldest/cheapest/expensive)
        limit: محدودیت نتایج (برای autocomplete)
    """
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({
            'success': False,
            'error': 'حداقل ۲ کاراکتر وارد کنید'
        }, status=400)

    # جستجوی اصلی روی چند فیلد (با پشتیبانی ی/ک عربی و فارسی)
    products = Product.objects.filter(
        build_search_q(query)
    ).filter(
        status__in=['available', 'coming_soon', 'exhibition']
    ).select_related(
        'album__manufacturer',
        'background_color',
        'weave_type',
        'feature',
    ).prefetch_related(
        'design_type', 'images'
    ).distinct()

    # فیلترهای اضافی
    manufacturer = request.GET.get('manufacturer')
    if manufacturer:
        products = products.filter(album__manufacturer_id=manufacturer)

    comb = request.GET.get('comb')
    if comb:
        products = products.filter(album__comb=comb)

    color = request.GET.get('color')
    if color:
        products = products.filter(background_color_id=color)

    design = request.GET.get('design')
    if design:
        products = products.filter(design_type__id=design)

    weave = request.GET.get('weave')
    if weave:
        products = products.filter(weave_type_id=weave)

    status = request.GET.get('status')
    if status and status in ['available', 'unavailable', 'exhibition', 'coming_soon']:
        products = products.filter(status=status)

    # مرتب‌سازی
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        products = products.order_by('created_at')
    elif sort == 'cheapest':
        products = products.order_by('album__base_price_12m', 'purchase_price_12m')
    elif sort == 'expensive':
        products = products.order_by('-album__base_price_12m', '-purchase_price_12m')
    elif sort == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('-created_at')

    # بررسی limit (حالت autocomplete)
    limit = request.GET.get('limit')
    if limit:
        try:
            limit = min(int(limit), 10)
        except (ValueError, TypeError):
            limit = 5
        products = products[:limit]
        results = []
        for p in products:
            img = p.primary_image
            thumb_url = None
            if img:
                if img.thumbnail:
                    thumb_url = img.thumbnail.url
                elif img.original:
                    thumb_url = img.original.url

            results.append({
                'id': p.id,
                'name': p.name,
                'title': p.display_title,
                'slug': p.slug,
                'manufacturer': p.album.manufacturer.name,
                'comb': p.comb,
                'price_12m': int(p.get_sell_price_12m()),
                'color': p.background_color.name if p.background_color else None,
                'thumbnail': thumb_url,
                'url': f'/farsh/{p.slug}/',
            })
        return JsonResponse({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        })

    # صفحه‌بندی
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = min(int(per_page), 50)
    except (ValueError, TypeError):
        per_page = 20

    paginator = Paginator(products, per_page)
    page = request.GET.get('page', '1')
    page_obj = paginator.get_page(page)

    results = []
    for p in page_obj:
        img = p.primary_image
        thumb_url = None
        if img:
            if img.thumbnail:
                thumb_url = img.thumbnail.url
            elif img.original:
                thumb_url = img.original.url

        results.append({
            'id': p.id,
            'name': p.name,
            'title': p.display_title,
            'slug': p.slug,
            'manufacturer': p.album.manufacturer.name,
            'album': p.album.name,
            'comb': p.comb,
            'price_12m': int(p.get_sell_price_12m()),
            'color': p.background_color.name if p.background_color else None,
            'design': p.design_type_display,
            'status': p.get_status_display(),
            'thumbnail': thumb_url,
            'url': f'/farsh/{p.slug}/',
        })

    return JsonResponse({
        'success': True,
        'query': query,
        'count': paginator.count,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'results': results
    })
