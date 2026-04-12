"""
فاز 11: کاتالوگ هوشمند و اشتراک‌گذاری
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from .models import Catalog
from products.models import Product


def catalog_view(request, code):
    """نمایش کاتالوگ عمومی"""
    catalog = get_object_or_404(Catalog, unique_code=code)
    
    # بررسی انقضا
    if catalog.is_expired():
        return render(request, 'catalog_app/expired.html', {'catalog': catalog})
    
    # افزایش بازدید
    catalog.increment_view()
    
    # دریافت محصولات
    products = catalog.products.select_related(
        'album__manufacturer',
        'background_color',
        'design_type'
    ).prefetch_related('images').filter(
        status='available'
    )
    
    context = {
        'catalog': catalog,
        'products': products,
        'share_url': request.build_absolute_uri(),
    }
    
    return render(request, 'catalog_app/catalog_view.html', context)


@staff_member_required
def catalog_create(request):
    """ایجاد کاتالوگ جدید"""
    if request.method == 'POST':
        title = request.POST.get('title', 'کاتالوگ جدید')
        product_ids = request.POST.getlist('products')
        
        if not product_ids:
            messages.error(request, 'لطفاً حداقل یک محصول انتخاب کنید.')
            return redirect('catalog_app:create')
        
        # ایجاد کاتالوگ
        catalog = Catalog.objects.create(
            title=title,
            created_by=request.user
        )
        
        # اضافه کردن محصولات
        products = Product.objects.filter(id__in=product_ids)
        catalog.products.set(products)
        
        messages.success(
            request,
            f'کاتالوگ «{catalog.title}» با {products.count()} محصول ایجاد شد.'
        )
        
        # نمایش لینک
        return redirect('catalog_app:success', code=catalog.unique_code)
    
    # نمایش فرم
    products = Product.objects.filter(
        status='available'
    ).select_related(
        'album__manufacturer'
    ).prefetch_related('images').order_by('-created_at')[:100]
    
    context = {'products': products}
    return render(request, 'catalog_app/catalog_create.html', context)


@staff_member_required
def catalog_success(request, code):
    """نمایش لینک کاتالوگ"""
    catalog = get_object_or_404(Catalog, unique_code=code)
    
    catalog_url = request.build_absolute_uri(
        reverse('catalog_app:view', kwargs={'code': code})
    )
    
    # لینک‌های اشتراک‌گذاری
    share_text = f"کاتالوگ {catalog.title} - همیار فرش"
    
    telegram_url = f"https://t.me/share/url?url={catalog_url}&text={share_text}"
    whatsapp_url = f"https://wa.me/?text={share_text} {catalog_url}"
    
    context = {
        'catalog': catalog,
        'catalog_url': catalog_url,
        'telegram_url': telegram_url,
        'whatsapp_url': whatsapp_url,
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
    
    product_url = request.build_absolute_uri(
        reverse('shop:product_detail', kwargs={'slug': slug})
    )
    
    share_text = f"{product.name} - {product.album.manufacturer.name}"
    
    telegram_url = f"https://t.me/share/url?url={product_url}&text={share_text}"
    whatsapp_url = f"https://wa.me/?text={share_text} {product_url}"
    
    context = {
        'product': product,
        'product_url': product_url,
        'telegram_url': telegram_url,
        'whatsapp_url': whatsapp_url,
        'share_text': share_text,
    }
    
    return render(request, 'catalog_app/product_share.html', context)
