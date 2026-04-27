"""
فاز 11: کاتالوگ هوشمند و اشتراک‌گذاری
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

from .models import Catalog
from products.models import Product
from catalog.models import (
    Manufacturer, Album, BackgroundColor, DesignType,
    WeaveType, Feature, ColorTone
)


def catalog_view(request, code):
    """نمایش کاتالوگ عمومی"""
    catalog = get_object_or_404(Catalog, unique_code=code)

    if catalog.is_expired():
        return render(request, 'catalog_app/expired.html', {'catalog': catalog})

    catalog.increment_view()

    products = catalog.products.select_related(
        'album__manufacturer', 'background_color', 'weave_type'
    ).prefetch_related('design_type', 'images').filter(status='available')

    context = {
        'catalog': catalog,
        'products': products,
        'share_url': request.build_absolute_uri(),
    }
    return render(request, 'catalog_app/catalog_view.html', context)


@staff_member_required
def catalog_create(request):
    """ایجاد کاتالوگ جدید — با فیلترهای پیشرفته"""
    if request.method == 'POST':
        title = request.POST.get('title', 'کاتالوگ جدید')
        product_ids = request.POST.getlist('products')

        if not product_ids:
            messages.error(request, 'لطفاً حداقل یک محصول انتخاب کنید.')
            return redirect('catalog_app:create')

        catalog = Catalog.objects.create(title=title, created_by=request.user)
        products = Product.objects.filter(id__in=product_ids)
        catalog.products.set(products)

        messages.success(request, f'کاتالوگ «{catalog.title}» با {products.count()} محصول ایجاد شد.')
        return redirect('catalog_app:success', code=catalog.unique_code)

    # محصولات با فیلتر
    products = Product.objects.filter(
        status__in=['available', 'coming_soon', 'exhibition']
    ).select_related(
        'album__manufacturer', 'background_color', 'weave_type', 'feature'
    ).prefetch_related('design_type', 'images')

    # اعمال فیلترها
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(album__name__icontains=q) |
            Q(album__manufacturer__name__icontains=q)
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

    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)

    products = products.order_by('-created_at')

    context = {
        'products': products,
        'total': products.count(),
        'query': q,
        # داده‌های فیلتر
        'manufacturers': Manufacturer.objects.filter(is_active=True).order_by('name'),
        'comb_choices': Album.COMB_CHOICES,
        'colors': BackgroundColor.objects.filter(is_active=True).order_by('name'),
        'designs': DesignType.objects.filter(is_active=True).order_by('name'),
        'weaves': WeaveType.objects.filter(is_active=True).order_by('name'),
        'features': Feature.objects.filter(is_active=True).order_by('name'),
        'tones': ColorTone.objects.filter(is_active=True).order_by('name'),
        'status_choices': Product.Status.choices,
        # مقادیر فعلی
        'sel_manufacturer': manufacturer or '',
        'sel_comb': comb or '',
        'sel_color': color or '',
        'sel_design': design or '',
        'sel_weave': weave or '',
        'sel_feature': feature or '',
        'sel_tone': tone or '',
        'sel_status': status or '',
    }
    return render(request, 'catalog_app/catalog_create.html', context)


@staff_member_required
def catalog_success(request, code):
    """نمایش لینک کاتالوگ"""
    catalog = get_object_or_404(Catalog, unique_code=code)
    catalog_url = request.build_absolute_uri(reverse('catalog_app:view', kwargs={'code': code}))
    share_text = f"کاتالوگ {catalog.title} - همیار فرش"

    context = {
        'catalog': catalog,
        'catalog_url': catalog_url,
        'telegram_url': f"https://t.me/share/url?url={catalog_url}&text={share_text}",
        'whatsapp_url': f"https://wa.me/?text={share_text} {catalog_url}",
        'share_text': share_text,
    }
    return render(request, 'catalog_app/catalog_success.html', context)


@staff_member_required
def catalog_list(request):
    """لیست کاتالوگ‌ها"""
    catalogs = Catalog.objects.prefetch_related('products').order_by('-created_at')
    context = {'catalogs': catalogs}
    return render(request, 'catalog_app/catalog_list.html', context)


@staff_member_required
def catalog_delete(request, pk):
    """حذف کاتالوگ"""
    catalog = get_object_or_404(Catalog, pk=pk)
    if request.method == 'POST':
        title = catalog.title
        catalog.delete()
        messages.success(request, f'کاتالوگ «{title}» حذف شد.')
        return redirect('catalog_app:list')
    context = {'catalog': catalog}
    return render(request, 'catalog_app/catalog_delete.html', context)


def product_share(request, slug):
    """اشتراک‌گذاری محصول تکی"""
    product = get_object_or_404(
        Product.objects.select_related('album__manufacturer').prefetch_related('images'),
        slug=slug
    )
    product_url = request.build_absolute_uri(reverse('shop:product_detail', kwargs={'slug': slug}))
    share_text = f"{product.name} - {product.album.manufacturer.name}"

    context = {
        'product': product,
        'product_url': product_url,
        'telegram_url': f"https://t.me/share/url?url={product_url}&text={share_text}",
        'whatsapp_url': f"https://wa.me/?text={share_text} {product_url}",
        'share_text': share_text,
    }
    return render(request, 'catalog_app/product_share.html', context)
