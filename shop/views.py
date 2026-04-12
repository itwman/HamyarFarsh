"""
فاز 6: ویترین وب‌سایت (سمت مشتری)
- صفحه اصلی کاتالوگ با فیلتر پیشرفته
- صفحه جزئیات محصول + SEO کامل + Schema.org
- سیستم امتیازدهی ستاره‌ای
- سفارش سایز خاص
"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from products.models import Product, ProductImage, ProductRating, ProductSizeRule
from catalog.models import (
    BackgroundColor, DesignType, WeaveType, Feature,
    ColorTone, CarpetSize, Manufacturer, Album
)
from settings_app.models import SiteSettings


def catalog_view(request):
    """صفحه کاتالوگ با فیلتر پیشرفته - موبایل فرندلی"""
    products = Product.objects.filter(
        status__in=['available', 'coming_soon', 'exhibition']
    ).select_related(
        'album__manufacturer', 'background_color',
        'weave_type', 'feature'
    ).prefetch_related('design_type', 'images')

    # فیلترها
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(album__name__icontains=q) |
            Q(album__manufacturer__name__icontains=q) |
            Q(background_color__name__icontains=q) |
            Q(design_type__name__icontains=q)
        )

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

    feature = request.GET.get('feature')
    if feature:
        products = products.filter(feature_id=feature)

    tone = request.GET.get('tone')
    if tone:
        products = products.filter(color_tone_id=tone)

    # مرتب‌سازی
    sort = request.GET.get('sort', 'newest')
    if sort == 'cheapest':
        products = products.order_by('album__base_price_12m', 'purchase_price_12m')
    elif sort == 'expensive':
        products = products.order_by('-album__base_price_12m', '-purchase_price_12m')
    elif sort == 'popular':
        products = products.order_by('-view_count')
    elif sort == 'rating':
        products = products.order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 24)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    # داده‌های فیلتر
    context = {
        'products': products_page,
        'total': paginator.count,
        'query': q,
        'current_sort': sort,
        'colors': BackgroundColor.objects.filter(is_active=True),
        'designs': DesignType.objects.filter(is_active=True),
        'weaves': WeaveType.objects.filter(is_active=True),
        'features': Feature.objects.filter(is_active=True),
        'tones': ColorTone.objects.filter(is_active=True),
        'manufacturers': Manufacturer.objects.filter(is_active=True),
        'comb_choices': Album.COMB_CHOICES,
        # مقادیر فعلی فیلتر
        'sel_manufacturer': manufacturer or '',
        'sel_comb': comb or '',
        'sel_color': color or '',
        'sel_design': design or '',
        'sel_weave': weave or '',
        'sel_feature': feature or '',
        'sel_tone': tone or '',
    }

    return render(request, 'shop/catalog.html', context)


def product_detail_view(request, slug):
    """صفحه جزئیات محصول + SEO کامل + Schema.org استاندارد + امتیاز"""
    product = get_object_or_404(
        Product.objects.select_related(
            'album__manufacturer', 'background_color',
            'weave_type', 'feature', 'color_tone'
        ).prefetch_related('design_type'),
        slug=slug
    )

    # اخیراً بازدیدشده (فاز 18)
    from wishlist.views import add_to_recently_viewed
    add_to_recently_viewed(request, product.pk)

    # تنظیمات سایت
    ss = SiteSettings.get_solo()

    # افزایش بازدید
    Product.objects.filter(pk=product.pk).update(view_count=product.view_count + 1)

    # تصاویر و ویدیوها
    images = product.images.all()
    videos = product.videos.filter(processing_status='completed')

    # جدول قیمت
    size_prices = product.get_all_size_prices()
    sell_12 = product.get_sell_price_12m()

    # کمترین و بیشترین قیمت (برای AggregateOffer)
    prices = [sp['price'] for sp in size_prices if sp['price'] > 0]
    low_price = min(prices) if prices else 0
    high_price = max(prices) if prices else sell_12

    # نظرات تأیید شده
    reviews = product.ratings.filter(
        status='approved'
    ).select_related('user').order_by('-created_at')[:20]

    # بررسی آیا کاربر قبلا امتیاز داده
    user_rating = None
    if request.user.is_authenticated:
        user_rating = product.ratings.filter(user=request.user).first()

    # محصولات مشابه
    related = Product.objects.filter(
        status='available',
        album__comb=product.album.comb,
    ).exclude(pk=product.pk).select_related(
        'album__manufacturer'
    ).prefetch_related('images')[:8]

    # URL کامل صفحه
    page_url = request.build_absolute_uri()

    # ===== Schema.org JSON-LD استاندارد =====
    schema_data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.display_title,
        "description": product.get_effective_seo_description(),
        "url": page_url,
        "sku": f"HF-{product.pk}",
        "mpn": f"HF-{product.pk}",
        "productID": str(product.pk),
        "brand": {
            "@type": "Brand",
            "name": product.manufacturer.name
        },
        "manufacturer": {
            "@type": "Organization",
            "name": product.manufacturer.name
        },
        "category": "فرش ماشینی",
        "material": product.yarn_type,
    }

    # تصاویر
    image_urls = []
    for img in images[:5]:
        if img.featured_image:
            image_urls.append(request.build_absolute_uri(img.featured_image.url))
        elif img.original:
            image_urls.append(request.build_absolute_uri(img.original.url))
    if image_urls:
        schema_data["image"] = image_urls

    # رنگ
    if product.background_color:
        schema_data["color"] = product.background_color.name

    # وزن
    if product.weight_class:
        schema_data["weight"] = {
            "@type": "QuantitativeValue",
            "name": product.weight_class
        }

    # ویژگی‌های اضافی
    additional_props = []
    additional_props.append({"@type": "PropertyValue", "name": "شانه", "value": str(product.album.comb)})
    if product.density:
        additional_props.append({"@type": "PropertyValue", "name": "تراکم", "value": str(product.density)})
    if product.design_type_display:
        additional_props.append({"@type": "PropertyValue", "name": "نوع طرح", "value": product.design_type_display})
    if product.weave_type:
        additional_props.append({"@type": "PropertyValue", "name": "نوع بافت", "value": product.weave_type.name})
    if product.feature:
        additional_props.append({"@type": "PropertyValue", "name": "ویژگی", "value": product.feature.name})
    if additional_props:
        schema_data["additionalProperty"] = additional_props

    # Offers - AggregateOffer (چند سایز با قیمت‌های مختلف)
    availability_url = "https://schema.org/InStock" if product.status == 'available' else (
        "https://schema.org/PreOrder" if product.status == 'coming_soon' else "https://schema.org/OutOfStock"
    )

    if len(prices) > 1:
        schema_data["offers"] = {
            "@type": "AggregateOffer",
            "url": page_url,
            "priceCurrency": "IRR",
            "lowPrice": low_price,
            "highPrice": high_price,
            "offerCount": len(prices),
            "availability": availability_url,
            "seller": {
                "@type": "Organization",
                "name": ss.site_name or "همیار فرش"
            }
        }
    elif sell_12:
        schema_data["offers"] = {
            "@type": "Offer",
            "url": page_url,
            "priceCurrency": "IRR",
            "price": sell_12,
            "availability": availability_url,
            "seller": {
                "@type": "Organization",
                "name": ss.site_name or "همیار فرش"
            }
        }

    # AggregateRating
    if product.avg_rating > 0 and product.rating_count > 0:
        schema_data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": float(product.avg_rating),
            "bestRating": 5,
            "worstRating": 1,
            "ratingCount": product.rating_count,
            "reviewCount": reviews.count()
        }

    # Review — نظرات تأییدشده به‌عنوان Schema Review
    review_schemas = []
    for r in reviews[:10]:
        review_schema = {
            "@type": "Review",
            "author": {
                "@type": "Person",
                "name": r.user.get_full_name() or "کاربر"
            },
            "datePublished": r.created_at.strftime('%Y-%m-%d'),
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": r.rating,
                "bestRating": 5,
                "worstRating": 1
            }
        }
        if r.comment:
            review_schema["reviewBody"] = r.comment
        review_schemas.append(review_schema)

    if review_schemas:
        schema_data["review"] = review_schemas

    context = {
        'product': product,
        'images': images,
        'videos': videos,
        'size_prices': size_prices,
        'sell_12': sell_12,
        'sell_price_12m': sell_12,
        'low_price': low_price,
        'high_price': high_price,
        'reviews': reviews,
        'user_rating': user_rating,
        'related': related,
        'ss': ss,
        'schema_json': json.dumps(schema_data, ensure_ascii=False),
    }

    return render(request, 'shop/product_detail.html', context)


@login_required
def submit_rating(request, product_id):
    """ثبت امتیاز و نظر کاربر"""
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط POST'}, status=400)

    product = get_object_or_404(Product, pk=product_id)
    rating_value = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if not rating_value or not rating_value.isdigit():
        return JsonResponse({'error': 'امتیاز معتبر نیست'}, status=400)

    rating_value = int(rating_value)
    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'error': 'امتیاز باید بین 1 تا 5 باشد'}, status=400)

    # بروزرسانی یا ایجاد
    rating_obj, created = ProductRating.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating_value,
            'comment': comment,
            'status': 'pending'
        }
    )

    if created:
        msg = 'نظر شما با موفقیت ثبت شد و پس از تأیید نمایش داده می‌شود.'
    else:
        msg = 'نظر شما بروزرسانی شد.'

    return JsonResponse({'success': True, 'message': msg})


@login_required
def custom_size_request(request):
    """درخواست سایز خاص"""
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط POST'}, status=400)

    product_id = request.POST.get('product_id')
    length = request.POST.get('length')
    width = request.POST.get('width')
    quantity = request.POST.get('quantity', '1')

    if not all([product_id, length, width]):
        return JsonResponse({'error': 'اطلاعات ناقص است'}, status=400)

    product = get_object_or_404(Product, pk=product_id)

    # ذخیره در session برای استفاده در سبد خرید
    request.session['custom_size_request'] = {
        'product_id': product_id,
        'product_name': product.name,
        'length': length,
        'width': width,
        'quantity': quantity,
    }

    messages.success(request, f'درخواست سایز {length}×{width} متر ثبت شد. به سبد خرید اضافه کنید.')

    return JsonResponse({
        'success': True,
        'message': 'درخواست ثبت شد',
        'redirect': request.POST.get('next', '/')
    })
