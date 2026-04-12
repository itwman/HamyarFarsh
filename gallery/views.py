"""
گالری تصاویر و ویدیو - همیار فرش
- گالری ویدیو (YouTube/آپارات استایل)
- گالری تصاویر (Pinterest استایل)
- فیلترهای هوشمند + SEO + Schema.org
"""
import json
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, F
from django.views.decorators.http import require_GET
from products.models import Product, ProductImage, ProductVideo
from catalog.models import (
    BackgroundColor, DesignType, WeaveType, Feature,
    ColorTone, Album, Manufacturer
)
from settings_app.models import SiteSettings


def _get_filter_data():
    """داده‌های مشترک فیلترها"""
    return {
        'colors': BackgroundColor.objects.filter(is_active=True).order_by('name'),
        'designs': DesignType.objects.filter(is_active=True).order_by('name'),
        'weaves': WeaveType.objects.filter(is_active=True).order_by('name'),
        'features': Feature.objects.filter(is_active=True).order_by('name'),
        'comb_choices': Album.COMB_CHOICES,
        'manufacturers': Manufacturer.objects.filter(is_active=True).order_by('name'),
    }


def _apply_product_filters(queryset, request):
    """اعمال فیلترهای مشترک محصول روی queryset ویدیو/تصویر"""
    filters = {}

    color = request.GET.get('color')
    if color:
        filters['product__background_color_id'] = color

    design = request.GET.get('design')
    if design:
        filters['product__design_type__id'] = design

    weave = request.GET.get('weave')
    if weave:
        filters['product__weave_type_id'] = weave

    feature = request.GET.get('feature')
    if feature:
        filters['product__feature_id'] = feature

    comb = request.GET.get('comb')
    if comb:
        filters['product__album__comb'] = comb

    manufacturer = request.GET.get('manufacturer')
    if manufacturer:
        filters['product__album__manufacturer_id'] = manufacturer

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(product__name__icontains=q) |
            Q(product__album__name__icontains=q) |
            Q(product__album__manufacturer__name__icontains=q) |
            Q(product__background_color__name__icontains=q) |
            Q(product__design_type__name__icontains=q)
        )

    if filters:
        queryset = queryset.filter(**filters)

    return queryset


def _get_active_filters(request):
    """مقادیر فیلتر فعلی"""
    return {
        'sel_color': request.GET.get('color', ''),
        'sel_design': request.GET.get('design', ''),
        'sel_weave': request.GET.get('weave', ''),
        'sel_feature': request.GET.get('feature', ''),
        'sel_comb': request.GET.get('comb', ''),
        'sel_manufacturer': request.GET.get('manufacturer', ''),
        'query': request.GET.get('q', '').strip(),
    }


# ===================================================================
#  گالری ویدیو
# ===================================================================

def video_gallery(request):
    """صفحه اصلی گالری ویدیو"""
    videos = ProductVideo.objects.filter(
        processing_status='completed',
        show_in_gallery=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).select_related(
        'product__album__manufacturer',
        'product__background_color',
        'product__weave_type',
        'product__feature',
    ).prefetch_related(
        'product__design_type',
    ).order_by('-is_featured', '-uploaded_at')

    # فیلترها
    videos = _apply_product_filters(videos, request)

    # مرتب‌سازی
    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        videos = videos.order_by('-view_count')
    elif sort == 'oldest':
        videos = videos.order_by('uploaded_at')
    # default: newest (already ordered)

    # صفحه‌بندی
    paginator = Paginator(videos, 12)
    page = request.GET.get('page')
    videos_page = paginator.get_page(page)

    # تعداد ویدیو برای هر فیلتر
    context = {
        'videos': videos_page,
        'total': paginator.count,
        'current_sort': sort,
        **_get_filter_data(),
        **_get_active_filters(request),
    }

    return render(request, 'gallery/video_gallery.html', context)


def video_detail(request, pk):
    """صفحه تک ویدیو"""
    video = get_object_or_404(
        ProductVideo.objects.select_related(
            'product__album__manufacturer',
            'product__background_color',
            'product__weave_type',
            'product__feature',
        ).prefetch_related(
            'product__design_type',
        ),
        pk=pk,
        processing_status='completed',
    )

    # افزایش بازدید
    ProductVideo.objects.filter(pk=pk).update(view_count=F('view_count') + 1)

    # ویدیوهای مشابه
    similar_videos = video.get_similar_videos(limit=6)

    # قیمت محصول
    sell_12 = video.product.get_sell_price_12m()

    # Schema.org VideoObject
    schema_data = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": video.get_effective_seo_title(),
        "description": video.get_effective_seo_description(),
        "uploadDate": video.uploaded_at.isoformat() if video.uploaded_at else '',
        "contentUrl": request.build_absolute_uri(video.get_best_quality_url()) if video.get_best_quality_url() else '',
    }
    if video.thumbnail:
        schema_data["thumbnailUrl"] = request.build_absolute_uri(video.thumbnail.url)
    if video.duration:
        # ISO 8601 duration
        mins = int(video.duration // 60)
        secs = int(video.duration % 60)
        schema_data["duration"] = f"PT{mins}M{secs}S"

    context = {
        'video': video,
        'product': video.product,
        'similar_videos': similar_videos,
        'sell_12': sell_12,
        'schema_json': json.dumps(schema_data, ensure_ascii=False),
    }

    return render(request, 'gallery/video_detail.html', context)


# ===================================================================
#  گالری تصاویر
# ===================================================================

def image_gallery(request):
    """صفحه اصلی گالری تصاویر (Pinterest استایل)"""
    images = ProductImage.objects.filter(
        is_primary=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).select_related(
        'product__album__manufacturer',
        'product__background_color',
        'product__weave_type',
        'product__feature',
        'product__color_tone',
    ).prefetch_related(
        'product__design_type',
    ).order_by('-product__is_featured', '-uploaded_at')

    # فیلترها
    images = _apply_product_filters(images, request)

    # مرتب‌سازی
    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        images = images.order_by('-product__view_count')
    elif sort == 'cheapest':
        images = images.order_by('product__album__base_price_12m')
    elif sort == 'expensive':
        images = images.order_by('-product__album__base_price_12m')
    elif sort == 'rating':
        images = images.order_by('-product__avg_rating')

    # صفحه‌بندی
    paginator = Paginator(images, 24)
    page = request.GET.get('page')
    images_page = paginator.get_page(page)

    context = {
        'images': images_page,
        'total': paginator.count,
        'current_sort': sort,
        **_get_filter_data(),
        **_get_active_filters(request),
    }

    return render(request, 'gallery/image_gallery.html', context)


def image_detail(request, pk):
    """صفحه جزئیات تصویر + تصاویر مشابه با امتیازدهی (سبک Pinterest)"""
    image = get_object_or_404(
        ProductImage.objects.select_related(
            'product__album__manufacturer',
            'product__background_color',
            'product__weave_type',
            'product__feature',
            'product__color_tone',
        ).prefetch_related('product__design_type'),
        pk=pk,
        is_primary=True,
    )
    product = image.product

    # افزایش بازدید
    Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)

    # قیمت
    sell_12 = product.get_sell_price_12m()

    # تصاویر مشابه با الگوریتم امتیازدهی
    similar_images = _get_similar_images(product, exclude_pk=pk, limit=12)

    context = {
        'image': image,
        'product': product,
        'sell_12': sell_12,
        'similar_images': similar_images,
    }
    return render(request, 'gallery/image_detail.html', context)


def _get_similar_images(product, exclude_pk, limit=12):
    """
    الگوریتم امتیازدهی شباهت بر اساس ویژگی‌های محصول
    
    امتیازدهی:
    - همان آلبوم: 5 امتیاز (بالاترین — حتماً شانه/تراکم/جنس‌نخ/شرکت یکیه)
    - همان شانه: 3 امتیاز
    - همان رنگ زمینه: 3 امتیاز
    - همان نوع طرح (یکی از طرح‌ها مشترک): 3 امتیاز
    - همان نوع بافت: 2 امتیاز
    - همان ویژگی: 2 امتیاز
    - همان تناژ رنگ: 1 امتیاز
    - همان شرکت: 1 امتیاز
    """
    from django.db.models import Case, When, IntegerField, Value, Sum

    design_ids = list(product.design_type.values_list('id', flat=True))

    candidates = ProductImage.objects.filter(
        is_primary=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).exclude(pk=exclude_pk).select_related(
        'product__album__manufacturer',
        'product__background_color',
        'product__weave_type',
        'product__feature',
        'product__color_tone',
    ).prefetch_related('product__design_type')

    # ساخت امتیاز شباهت با annotation
    score_cases = []

    # همان آلبوم (5 امتیاز)
    score_cases.append(
        Case(When(product__album=product.album, then=Value(5)), default=Value(0), output_field=IntegerField())
    )

    # همان شانه (3 امتیاز)
    score_cases.append(
        Case(When(product__album__comb=product.album.comb, then=Value(3)), default=Value(0), output_field=IntegerField())
    )

    # همان رنگ زمینه (3 امتیاز)
    if product.background_color_id:
        score_cases.append(
            Case(When(product__background_color=product.background_color, then=Value(3)), default=Value(0), output_field=IntegerField())
        )

    # همان نوع طرح (3 امتیاز — M2M)
    if design_ids:
        score_cases.append(
            Case(When(product__design_type__id__in=design_ids, then=Value(3)), default=Value(0), output_field=IntegerField())
        )

    # همان نوع بافت (2 امتیاز)
    if product.weave_type_id:
        score_cases.append(
            Case(When(product__weave_type=product.weave_type, then=Value(2)), default=Value(0), output_field=IntegerField())
        )

    # همان ویژگی (2 امتیاز)
    if product.feature_id:
        score_cases.append(
            Case(When(product__feature=product.feature, then=Value(2)), default=Value(0), output_field=IntegerField())
        )

    # همان تناژ رنگ (1 امتیاز)
    if product.color_tone_id:
        score_cases.append(
            Case(When(product__color_tone=product.color_tone, then=Value(1)), default=Value(0), output_field=IntegerField())
        )

    # همان شرکت (1 امتیاز)
    score_cases.append(
        Case(When(product__album__manufacturer=product.album.manufacturer, then=Value(1)), default=Value(0), output_field=IntegerField())
    )

    # اعمال امتیازدهی و مرتب‌سازی
    candidates = candidates.annotate(
        similarity_score=sum(score_cases)
    ).filter(
        similarity_score__gt=0
    ).order_by('-similarity_score', '-product__view_count').distinct()[:limit]

    return candidates


@require_GET
def api_similar_images(request, pk):
    """API تصاویر مشابه (برای AJAX)"""
    image = get_object_or_404(ProductImage, pk=pk, is_primary=True)
    product = image.product

    similar = _get_similar_images(product, exclude_pk=pk, limit=12)

    data = []
    for img in similar:
        p = img.product
        data.append({
            'id': img.id,
            'src': img.featured_image.url if img.featured_image else (img.thumbnail.url if img.thumbnail else img.original.url),
            'alt': img.get_effective_alt(),
            'title': p.display_title,
            'comb': p.album.comb,
            'color': p.background_color.name if p.background_color else '',
            'design': p.design_type_display,
            'price': f'{p.get_sell_price_12m():,}' if p.get_sell_price_12m() else '',
            'url': f'/farsh/{p.slug}/',
            'detail_url': f'/gallery/images/{img.id}/',
            'score': getattr(img, 'similarity_score', 0),
        })

    return JsonResponse({'similar': data})


# ===================================================================
#  API Endpoints (AJAX فیلتر)
# ===================================================================

@require_GET
def api_videos_filter(request):
    """API فیلتر ویدیوها (برای AJAX)"""
    videos = ProductVideo.objects.filter(
        processing_status='completed',
        show_in_gallery=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).select_related(
        'product__album__manufacturer',
        'product__background_color',
    ).prefetch_related('product__design_type')

    videos = _apply_product_filters(videos, request)

    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        videos = videos.order_by('-view_count')
    else:
        videos = videos.order_by('-uploaded_at')

    paginator = Paginator(videos, 12)
    page = request.GET.get('page', 1)
    videos_page = paginator.get_page(page)

    data = []
    for v in videos_page:
        item = {
            'id': v.id,
            'title': v.get_effective_title(),
            'thumbnail': v.thumbnail.url if v.thumbnail else '',
            'duration': v.get_duration_display(),
            'view_count': v.view_count,
            'product_name': v.product.name,
            'product_url': f'/farsh/{v.product.slug}/',
            'detail_url': f'/gallery/videos/{v.id}/',
            'comb': v.product.album.comb,
            'color': v.product.background_color.name if v.product.background_color else '',
            'design': v.product.design_type_display,
        }
        data.append(item)

    return JsonResponse({
        'videos': data,
        'total': paginator.count,
        'has_next': videos_page.has_next(),
        'page': videos_page.number,
    })


@require_GET
def api_images_filter(request):
    """API فیلتر تصاویر (برای AJAX)"""
    images = ProductImage.objects.filter(
        is_primary=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).select_related(
        'product__album__manufacturer',
        'product__background_color',
    ).prefetch_related('product__design_type')

    images = _apply_product_filters(images, request)

    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        images = images.order_by('-product__view_count')
    else:
        images = images.order_by('-uploaded_at')

    paginator = Paginator(images, 24)
    page = request.GET.get('page', 1)
    images_page = paginator.get_page(page)

    data = []
    for img in images_page:
        p = img.product
        item = {
            'id': img.id,
            'src': img.featured_image.url if img.featured_image else img.original.url,
            'thumbnail': img.thumbnail.url if img.thumbnail else img.original.url,
            'alt': img.get_effective_alt(),
            'product_name': p.name,
            'product_url': f'/farsh/{p.slug}/',
            'comb': p.album.comb,
            'color': p.background_color.name if p.background_color else '',
            'design': p.design_type_display,
            'price': f'{p.get_sell_price_12m():,}' if p.get_sell_price_12m() else '',
        }
        data.append(item)

    return JsonResponse({
        'images': data,
        'total': paginator.count,
        'has_next': images_page.has_next(),
        'page': images_page.number,
    })


@require_GET
def api_similar_images(request, pk):
    """
    API تصاویر مشابه برای Lightbox بی‌نهایت
    امتیازدهی شباهت: رنگ=3, طرح=3, شانه=2, شرکت=1, آلبوم=2
    """
    try:
        current_img = ProductImage.objects.select_related(
            'product__album__manufacturer', 'product__background_color',
        ).prefetch_related('product__design_type').get(pk=pk)
    except ProductImage.DoesNotExist:
        return JsonResponse({'images': []})

    cp = current_img.product
    current_design_ids = set(cp.design_type.values_list('id', flat=True))

    # کاندیدها
    candidates = ProductImage.objects.filter(
        is_primary=True,
        product__status__in=['available', 'coming_soon', 'exhibition'],
    ).exclude(pk=pk).select_related(
        'product__album__manufacturer', 'product__background_color',
    ).prefetch_related('product__design_type')[:200]

    scored = []
    for img in candidates:
        p = img.product
        score = 0
        # رنگ زمینه یکسان
        if cp.background_color_id and p.background_color_id == cp.background_color_id:
            score += 3
        # طرح مشترک
        if current_design_ids:
            p_design_ids = set(p.design_type.values_list('id', flat=True))
            common = current_design_ids & p_design_ids
            if common:
                score += 3
        # شانه یکسان
        if p.album.comb == cp.album.comb:
            score += 2
        # آلبوم یکسان
        if p.album_id == cp.album_id:
            score += 2
        # شرکت یکسان
        if p.album.manufacturer_id == cp.album.manufacturer_id:
            score += 1

        scored.append((score, -p.view_count, img))

    # مرتب‌سازی: اول امتیاز بالاتر، بعد بازدید بیشتر
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # حداکثر 50 تصویر
    data = []
    for score, _, img in scored[:50]:
        p = img.product
        data.append({
            'id': img.id,
            'src': img.featured_image.url if img.featured_image else img.original.url,
            'alt': img.get_effective_alt(),
            'product_name': p.name,
            'display_title': p.display_title,
            'product_url': f'/farsh/{p.slug}/',
            'comb': f'{p.album.comb} شانه',
            'color': p.background_color.name if p.background_color else '',
            'design': p.design_type_display,
            'price': f'{p.get_sell_price_12m():,}' if p.get_sell_price_12m() else '',
        })

    return JsonResponse({'images': data})


def image_detail(request, pk):
    """Redirect به صفحه محصول (برای SEO)"""
    from django.shortcuts import redirect
    img = get_object_or_404(ProductImage, pk=pk)
    return redirect(f'/farsh/{img.product.slug}/')
