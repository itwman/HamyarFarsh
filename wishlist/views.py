"""
فاز 18: ویوهای علاقه‌مندی، مقایسه، اخیراً بازدیدشده
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import WishlistItem


# ===================================================================
#  علاقه‌مندی (Wishlist) — AJAX
# ===================================================================

@require_POST
def wishlist_toggle(request):
    """افزودن/حذف از علاقه‌مندی — AJAX"""
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'product_id الزامی است'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'محصول یافت نشد'}, status=404)

    if request.user.is_authenticated:
        # DB-based
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            item.delete()
            return JsonResponse({
                'action': 'removed',
                'message': f'«{product.name}» از علاقه‌مندی‌ها حذف شد.',
                'count': WishlistItem.objects.filter(user=request.user).count(),
            })
        return JsonResponse({
            'action': 'added',
            'message': f'«{product.name}» به علاقه‌مندی‌ها اضافه شد.',
            'count': WishlistItem.objects.filter(user=request.user).count(),
        })
    else:
        # localStorage-based (frontend handles it, this is fallback)
        return JsonResponse({
            'action': 'login_required',
            'message': 'برای ذخیره علاقه‌مندی ابتدا وارد شوید.',
        })


def wishlist_check(request):
    """بررسی آیا محصول در علاقه‌مندی هست — AJAX GET"""
    product_id = request.GET.get('product_id')
    if request.user.is_authenticated and product_id:
        exists = WishlistItem.objects.filter(user=request.user, product_id=product_id).exists()
        return JsonResponse({'in_wishlist': exists})
    return JsonResponse({'in_wishlist': False})


def wishlist_ids(request):
    """لیست ID محصولات علاقه‌مندی کاربر — برای بارگذاری اولیه"""
    if request.user.is_authenticated:
        ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
        return JsonResponse({'ids': ids})
    return JsonResponse({'ids': []})


@login_required
def wishlist_page(request):
    """صفحه لیست علاقه‌مندی‌ها"""
    items = WishlistItem.objects.filter(user=request.user).select_related(
        'product__album__manufacturer', 'product__background_color'
    ).prefetch_related('product__design_type', 'product__images')

    context = {
        'items': items,
        'count': items.count(),
    }
    return render(request, 'wishlist/wishlist_page.html', context)


# ===================================================================
#  مقایسه محصولات — Session-based (حداکثر 4)
# ===================================================================

COMPARE_SESSION_KEY = 'compare_products'
COMPARE_MAX = 4


@require_POST
def compare_toggle(request):
    """افزودن/حذف از لیست مقایسه — AJAX"""
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'product_id الزامی'}, status=400)

    product_id = int(product_id)
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])

    if product_id in compare_list:
        compare_list.remove(product_id)
        action = 'removed'
        msg = 'از مقایسه حذف شد.'
    else:
        if len(compare_list) >= COMPARE_MAX:
            return JsonResponse({
                'action': 'full',
                'message': f'حداکثر {COMPARE_MAX} محصول قابل مقایسه است. ابتدا یکی را حذف کنید.',
                'count': len(compare_list),
            })
        compare_list.append(product_id)
        action = 'added'
        msg = 'به مقایسه اضافه شد.'

    request.session[COMPARE_SESSION_KEY] = compare_list
    return JsonResponse({
        'action': action,
        'message': msg,
        'count': len(compare_list),
        'ids': compare_list,
    })


def compare_ids(request):
    """لیست ID های مقایسه — GET"""
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])
    return JsonResponse({'ids': compare_list, 'count': len(compare_list)})


def compare_clear(request):
    """پاک کردن لیست مقایسه"""
    request.session[COMPARE_SESSION_KEY] = []
    return JsonResponse({'success': True})


def compare_page(request):
    """صفحه مقایسه محصولات"""
    compare_list = request.session.get(COMPARE_SESSION_KEY, [])
    products = Product.objects.filter(pk__in=compare_list).select_related(
        'album__manufacturer', 'background_color', 'weave_type', 'feature', 'color_tone'
    ).prefetch_related('design_type', 'images')

    context = {
        'products': products,
        'count': len(compare_list),
    }
    return render(request, 'wishlist/compare_page.html', context)


# ===================================================================
#  اخیراً بازدیدشده — Session-based
# ===================================================================

RECENTLY_SESSION_KEY = 'recently_viewed'
RECENTLY_MAX = 12


def add_to_recently_viewed(request, product_id):
    """افزودن به لیست اخیراً بازدیدشده (فراخوانی از product_detail view)"""
    recently = request.session.get(RECENTLY_SESSION_KEY, [])
    product_id = int(product_id)
    if product_id in recently:
        recently.remove(product_id)
    recently.insert(0, product_id)
    request.session[RECENTLY_SESSION_KEY] = recently[:RECENTLY_MAX]


def get_recently_viewed(request):
    """دریافت محصولات اخیراً بازدیدشده"""
    recently = request.session.get(RECENTLY_SESSION_KEY, [])
    if not recently:
        return Product.objects.none()
    products = Product.objects.filter(pk__in=recently).select_related(
        'album__manufacturer', 'background_color'
    ).prefetch_related('images')
    # حفظ ترتیب session
    product_dict = {p.pk: p for p in products}
    return [product_dict[pid] for pid in recently if pid in product_dict]


def recently_viewed_api(request):
    """API محصولات اخیراً بازدیدشده — AJAX"""
    products = get_recently_viewed(request)
    data = []
    for p in products[:8]:
        img = p.primary_image
        data.append({
            'id': p.pk,
            'name': p.display_title,
            'url': f'/farsh/{p.slug}/',
            'thumbnail': img.thumbnail.url if img and img.thumbnail else '',
            'price': f'{p.get_sell_price_12m():,}' if p.get_sell_price_12m() else '',
        })
    return JsonResponse({'products': data})
