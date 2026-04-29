"""
فاز 9: پنل مدیریت محصولات
- لیست محصولات با فیلتر پیشرفته
- افزودن/ویرایش محصول
- آپلود تصاویر (تک و چندتایی)
- مدیریت قوانین سفارش سایزها
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from PIL import Image
import os
import sys

from .models import Product, ProductImage, ProductVideo, ProductSizeRule, TempUpload
from .forms import ProductForm, ProductImageForm, MultiImageUploadForm, ProductFilterForm, ProductVideoForm
from catalog.models import (
    Album, Manufacturer, BackgroundColor, DesignType,
    WeaveType, Feature, ColorTone, CarpetSize
)
from settings_app.models import SiteSettings


@staff_member_required
def product_list(request):
    """لیست محصولات با فیلتر پیشرفته - پنل مدیریت"""
    products = Product.objects.select_related(
        'album__manufacturer', 'background_color'
    ).prefetch_related('design_type', 'images').annotate(
        image_count=Count('images')
    )

    form = ProductFilterForm(request.GET)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(album__name__icontains=search) |
                Q(album__manufacturer__name__icontains=search)
            )
        manufacturer = form.cleaned_data.get('manufacturer')
        if manufacturer:
            products = products.filter(album__manufacturer=manufacturer)
        album = form.cleaned_data.get('album')
        if album:
            products = products.filter(album=album)
        comb = form.cleaned_data.get('comb')
        if comb:
            products = products.filter(album__comb=comb)
        status = form.cleaned_data.get('status')
        if status:
            products = products.filter(status=status)
        bg_color = form.cleaned_data.get('background_color')
        if bg_color:
            products = products.filter(background_color=bg_color)
        design = form.cleaned_data.get('design_type')
        if design:
            products = products.filter(design_type=design)

    sort = request.GET.get('sort', '-created_at')
    products = products.order_by(sort)

    paginator = Paginator(products, 30)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    context = {
        'products': products_page,
        'form': form,
        'total': paginator.count,
        'current_sort': sort,
    }

    return render(request, 'products/product_list.html', context)


@staff_member_required
def product_add(request):
    """افزودن محصول جدید - ابتدا تصاویر، سپس اطلاعات"""
    import uuid
    import shutil
    import os
    from django.core.files.base import ContentFile

    # دریافت یا ساخت session_key برای این صفحه
    upload_session_key = request.POST.get('upload_session_key') or request.GET.get('upload_session_key')
    if not upload_session_key:
        upload_session_key = str(uuid.uuid4())

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()

            # انتقال تصاویر موقت به محصول
            temp_uploads = TempUpload.objects.filter(
                session_key=upload_session_key,
                user=request.user
            ).order_by('order', 'created_at')

            settings_obj = SiteSettings.get_solo()
            transferred_count = 0

            for temp in temp_uploads:
                try:
                    # خوندن فایل و ساخت ProductImage
                    if temp.file and os.path.isfile(temp.file.path):
                        with open(temp.file.path, 'rb') as f:
                            content = ContentFile(f.read(), name=temp.original_name or os.path.basename(temp.file.name))
                        
                        img = ProductImage(
                            product=product,
                            original=content,
                            order=temp.order,
                            is_primary=temp.is_primary,
                        )
                        img.save()

                        # تولید تامبنیل و تصویر شاخص
                        try:
                            generate_thumbnails(img, settings_obj)
                            transferred_count += 1
                        except Exception as e:
                            messages.warning(request, f'خطا در پردازش تصویر: {str(e)}')
                except Exception as e:
                    messages.warning(request, f'خطا در انتقال تصویر: {str(e)}')

            # حذف رکوردهای موقت بعد از انتقال موفق
            for temp in temp_uploads:
                temp.delete()

            # اگر هیچ تصویر شاخصی تعیین نشده، اولین تصویر رو شاخص کن
            if not product.images.filter(is_primary=True).exists():
                first_img = product.images.first()
                if first_img:
                    first_img.is_primary = True
                    first_img.save()
                    settings_obj = SiteSettings.get_solo()
                    try:
                        generate_featured(first_img, settings_obj)
                    except Exception:
                        pass

            if transferred_count > 0:
                messages.success(
                    request,
                    f'محصول «{product.name}» با موفقیت ایجاد شد. {transferred_count} تصویر منتقل شد.'
                )
                # اگر تصاویر آپلود شده → برگرد به لیست محصولات
                return redirect('products:product_list')
            else:
                messages.warning(request, f'محصول «{product.name}» ایجاد شد ولی تصویری آپلود نشده بود. لطفاً تصاویر را آپلود کنید.')
                # فقط اگر تصویری آپلود نشد → برو به صفحه مدیریت رسانه
                return redirect('products:product_media', product.pk)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
    else:
        form = ProductForm()

    # تصاویر موقت فعلی در این سشن (اگر صفحه رو refresh کرده)
    temp_images = TempUpload.objects.filter(
        session_key=upload_session_key,
        user=request.user
    ).order_by('order', 'created_at')

    context = {
        'form': form,
        'title': 'افزودن محصول جدید',
        'action': 'add',
        'upload_session_key': upload_session_key,
        'temp_images': temp_images,
    }

    return render(request, 'products/product_form_with_upload.html', context)


@staff_member_required
def temp_upload(request):
    """AJAX endpoint برای آپلود تصاویر موقت (صفحه افزودن محصول)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'فقط POST مجاز است'}, status=405)

    session_key = request.POST.get('session_key', '').strip()
    if not session_key:
        return JsonResponse({'success': False, 'error': 'session_key لازم است'}, status=400)

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({'success': False, 'error': 'فایلی دریافت نشد'}, status=400)

    # تعداد فعلی برای order
    last_order = TempUpload.objects.filter(
        session_key=session_key, user=request.user
    ).count()

    uploaded = []
    errors = []

    for f in files:
        # اعتبارسنجی سایز (حداکثر 10MB)
        if f.size > 10 * 1024 * 1024:
            errors.append(f'فایل {f.name} بزرگتر از 10MB است')
            continue

        # اعتبارسنجی فرمت
        if not f.content_type or not f.content_type.startswith('image/'):
            errors.append(f'فایل {f.name} تصویر نیست')
            continue

        try:
            temp = TempUpload.objects.create(
                session_key=session_key,
                user=request.user,
                file=f,
                original_name=f.name,
                file_size=f.size,
                order=last_order,
                is_primary=(last_order == 0),  # اولین تصویر خودکار شاخص می‌شه
            )
            last_order += 1
            uploaded.append({
                'id': temp.id,
                'url': temp.file.url,
                'name': temp.original_name,
                'size': temp.file_size,
                'is_primary': temp.is_primary,
            })
        except Exception as e:
            errors.append(f'خطا در {f.name}: {str(e)}')

    return JsonResponse({
        'success': True,
        'uploaded': uploaded,
        'errors': errors,
    })


@staff_member_required
def temp_upload_delete(request, pk):
    """حذف تصویر موقت (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'فقط POST مجاز است'}, status=405)

    try:
        temp = TempUpload.objects.get(pk=pk, user=request.user)
        was_primary = temp.is_primary
        session_key = temp.session_key
        temp.delete()

        # اگر تصویر شاخص حذف شد، اولین تصویر باقیمانده رو شاخص کن
        if was_primary:
            first = TempUpload.objects.filter(
                session_key=session_key, user=request.user
            ).order_by('order', 'created_at').first()
            if first:
                first.is_primary = True
                first.save(update_fields=['is_primary'])

        return JsonResponse({'success': True})
    except TempUpload.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'تصویر یافت نشد'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@staff_member_required
def temp_upload_set_primary(request, pk):
    """تعیین تصویر شاخص در بین آپلودهای موقت (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'فقط POST مجاز است'}, status=405)

    try:
        temp = TempUpload.objects.get(pk=pk, user=request.user)
        # غیر شاخص کردن بقیه
        TempUpload.objects.filter(
            session_key=temp.session_key, user=request.user
        ).update(is_primary=False)
        # شاخص کردن این تصویر
        temp.is_primary = True
        temp.save(update_fields=['is_primary'])
        return JsonResponse({'success': True})
    except TempUpload.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'تصویر یافت نشد'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@staff_member_required
def product_add_OLD(request):
    """[بایگانی] افزودن محصول جدید - نسخه قدیمی"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'محصول «{product.name}» با موفقیت ایجاد شد.')
            return redirect('products:product_images', product.pk)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'افزودن محصول جدید',
        'action': 'add',
    }

    return render(request, 'products/product_form.html', context)


@staff_member_required
def product_edit(request, pk):
    """ویرایش محصول"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'محصول «{product.name}» بروزرسانی شد.')
            return redirect('products:product_list')
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': f'ویرایش {product.name}',
        'action': 'edit',
    }

    return render(request, 'products/product_form.html', context)


@staff_member_required
def product_delete(request, pk):
    """حذف محصول"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'محصول «{name}» حذف شد.')
        return redirect('products:product_list')

    context = {'product': product}
    return render(request, 'products/product_delete_confirm.html', context)


@staff_member_required
def product_images(request, pk):
    """مدیریت تصاویر محصول - آپلود تک و چندتایی"""
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all().order_by('order', 'uploaded_at')

    if request.method == 'POST':
        settings_obj = SiteSettings.get_solo()
        uploaded_count = 0

        files_list = request.FILES.getlist('images')
        if files_list:
            for file in files_list:
                img = ProductImage(product=product, original=file)
                img.save()
                try:
                    generate_thumbnails(img, settings_obj)
                    uploaded_count += 1
                except Exception as e:
                    messages.warning(request, f'خطا در پردازش {file.name}: {str(e)}')

            messages.success(request, f'{uploaded_count} تصویر با موفقیت آپلود شد.')
            return redirect('products:product_images', pk=pk)

        elif 'original' in request.FILES:
            form = ProductImageForm(request.POST, request.FILES)
            if form.is_valid():
                img = form.save(commit=False)
                img.product = product
                img.save()
                try:
                    generate_thumbnails(img, settings_obj)
                    messages.success(request, 'تصویر آپلود شد.')
                except Exception as e:
                    messages.warning(request, f'تصویر ذخیره شد ولی خطا در تولید تامبنیل: {str(e)}')
            else:
                messages.error(request, 'خطا در فرم: ' + str(form.errors))
            return redirect('products:product_images', pk=pk)

        else:
            messages.error(request, 'لطفاً یک فایل انتخاب کنید.')
            return redirect('products:product_images', pk=pk)

    single_form = ProductImageForm()
    multi_form = MultiImageUploadForm()

    context = {
        'product': product,
        'images': images,
        'single_form': single_form,
        'multi_form': multi_form,
    }

    return render(request, 'products/product_images.html', context)


@staff_member_required
def image_delete(request, pk):
    """حذف تصویر"""
    image = get_object_or_404(ProductImage, pk=pk)
    product_pk = image.product.pk

    if request.method == 'POST':
        try:
            if image.original and os.path.isfile(image.original.path):
                os.remove(image.original.path)
            if image.thumbnail and os.path.isfile(image.thumbnail.path):
                os.remove(image.thumbnail.path)
            if image.featured_image and os.path.isfile(image.featured_image.path):
                os.remove(image.featured_image.path)
        except:
            pass

        image.delete()
        messages.success(request, 'تصویر حذف شد.')

    return redirect('products:product_images', pk=product_pk)


@staff_member_required
def image_set_primary(request, pk):
    """تنظیم تصویر شاخص"""
    image = get_object_or_404(ProductImage, pk=pk)

    ProductImage.objects.filter(product=image.product).update(is_primary=False)
    image.is_primary = True
    image.save()

    # regenerate تصویر شاخص با کد جدید
    settings_obj = SiteSettings.get_solo()
    try:
        generate_featured(image, settings_obj)
        messages.success(request, 'تصویر شاخص تنظیم و ساخته شد.')
    except Exception as e:
        messages.warning(request, f'تصویر شاخص تنظیم شد ولی خطا در تولید: {str(e)}')

    return redirect('products:product_images', pk=image.product.pk)


@staff_member_required
def product_size_rules(request, pk):
    """مدیریت قوانین سفارش سایزها"""
    product = get_object_or_404(Product, pk=pk)
    sizes = CarpetSize.objects.filter(is_active=True).order_by('sort_order')

    if request.method == 'POST':
        for size in sizes:
            rule_key = f'rule_{size.id}'
            rule_value = request.POST.get(rule_key)

            if rule_value and rule_value != size.default_order_rule:
                ProductSizeRule.objects.update_or_create(
                    product=product,
                    carpet_size=size,
                    defaults={'order_rule': rule_value}
                )
            else:
                ProductSizeRule.objects.filter(
                    product=product, carpet_size=size
                ).delete()

        messages.success(request, 'قوانین سفارش بروزرسانی شد.')
        return redirect('products:product_list')

    existing_rules = {
        rule.carpet_size_id: rule.order_rule
        for rule in product.size_rules.all()
    }

    sizes_with_rules = []
    for size in sizes:
        current_rule = existing_rules.get(size.id, size.default_order_rule)
        sizes_with_rules.append({
            'size': size,
            'current_rule': current_rule,
            'is_custom': size.id in existing_rules,
        })

    context = {
        'product': product,
        'sizes_with_rules': sizes_with_rules,
    }

    return render(request, 'products/product_size_rules.html', context)


@staff_member_required
def bulk_price_update(request):
    """بروزرسانی انبوه قیمت‌ها"""
    if request.method == 'POST':
        album_id = request.POST.get('album')
        new_price = request.POST.get('new_price')

        if album_id and new_price:
            try:
                album = Album.objects.get(pk=album_id)
                old_price = album.base_price_12m
                album.base_price_12m = int(new_price)
                album.save()

                affected = Product.objects.filter(
                    album=album, purchase_price_12m__isnull=True
                ).count()

                messages.success(
                    request,
                    f'قیمت آلبوم «{album.name}» از {old_price:,} به {int(new_price):,} تومان تغییر کرد. '
                    f'{affected} محصول تأثیر می‌گیرند.'
                )
            except Album.DoesNotExist:
                messages.error(request, 'آلبوم یافت نشد.')
            except ValueError:
                messages.error(request, 'قیمت معتبر نیست.')
        else:
            messages.error(request, 'اطلاعات ناقص است.')

        return redirect('products:bulk_price_update')

    albums = Album.objects.filter(is_active=True).select_related('manufacturer')

    context = {'albums': albums}
    return render(request, 'products/bulk_price_update.html', context)


@staff_member_required
def product_media(request, pk):
    """مدیریت تصاویر و ویدیوهای محصول"""
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all().order_by('order', 'uploaded_at')
    videos = product.videos.all().order_by('order', '-uploaded_at')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'upload_video' and 'original_file' in request.FILES:
            video_form = ProductVideoForm(request.POST, request.FILES)
            if video_form.is_valid():
                video = video_form.save(commit=False)
                video.product = product
                video.save()
                messages.success(request, 'ویدیو آپلود شد. پردازش خودکار در حال انجام است...')
            else:
                messages.error(request, 'خطا در فرم ویدیو.')
            return redirect('products:product_media', pk=pk)

        elif action == 'upload_images':
            files_list = request.FILES.getlist('images')
            if files_list:
                settings_obj = SiteSettings.get_solo()
                count = 0
                for file in files_list:
                    img = ProductImage(product=product, original=file)
                    img.save()
                    try:
                        generate_thumbnails(img, settings_obj)
                        count += 1
                    except Exception as e:
                        messages.warning(request, f'خطا در پردازش {file.name}: {str(e)}')
                messages.success(request, f'{count} تصویر آپلود شد.')
            else:
                messages.error(request, 'لطفاً فایل انتخاب کنید.')
            return redirect('products:product_media', pk=pk)

        elif action == 'upload_single' and 'original' in request.FILES:
            form = ProductImageForm(request.POST, request.FILES)
            if form.is_valid():
                img = form.save(commit=False)
                img.product = product
                img.save()
                settings_obj = SiteSettings.get_solo()
                try:
                    generate_thumbnails(img, settings_obj)
                    messages.success(request, 'تصویر آپلود شد.')
                except Exception as e:
                    messages.warning(request, f'تصویر ذخیره شد ولی خطا در تولید تامبنیل: {str(e)}')
            return redirect('products:product_media', pk=pk)

    video_form = ProductVideoForm()
    single_form = ProductImageForm()
    multi_form = MultiImageUploadForm()

    context = {
        'product': product,
        'images': images,
        'videos': videos,
        'video_form': video_form,
        'single_form': single_form,
        'multi_form': multi_form,
    }
    return render(request, 'products/product_media.html', context)


@staff_member_required
def video_delete(request, pk):
    """حذف ویدیو"""
    video = get_object_or_404(ProductVideo, pk=pk)
    product_pk = video.product.pk

    if request.method == 'POST':
        for field in [video.original_file, video.video_720p, video.video_480p, video.thumbnail]:
            try:
                if field and os.path.isfile(field.path):
                    os.remove(field.path)
            except:
                pass
        video.delete()
        messages.success(request, 'ویدیو حذف شد.')

    return redirect('products:product_media', pk=product_pk)


# ============================================================
# Helper Functions
# ============================================================

def _is_linux():
    """تشخیص سیستم‌عامل"""
    return sys.platform.startswith('linux')


def generate_featured(product_image, settings_obj):
    """
    تولید تصویر شاخص — cross-platform:
    - لینوکس: از image_processing.py (cairo+pango) استفاده میکنه
    - ویندوز: از Pillow+arabic_reshaper استفاده میکنه
    """
    product = product_image.product
    slug = product.slug or f'product-{product.pk}'

    if _is_linux():
        # ===== لینوکس: cairo+pango =====
        from products.image_processing import generate_featured_image
        content = generate_featured_image(product_image.original.path, product)
        product_image.featured_image.save(f'{slug}-featured.jpg', content, save=False)
        product_image.save()
    else:
        # ===== ویندوز: Pillow+arabic_reshaper =====
        _generate_featured_windows(product_image, settings_obj)


def generate_thumbnails(product_image, settings_obj):
    """
    تولید تامبنیل + تصویر شاخص — cross-platform
    """
    from PIL import Image
    from io import BytesIO
    from django.core.files.base import ContentFile

    img_path = product_image.original.path
    img = Image.open(img_path)

    # تبدیل به RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    filename = os.path.basename(product_image.original.name)

    # ====== تامبنیل ======
    thumb_w = settings_obj.thumbnail_width or 350
    thumb_h = settings_obj.thumbnail_height or 350
    img_thumb = img.copy()
    img_thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)

    thumb_io = BytesIO()
    img_thumb.save(thumb_io, format='JPEG', quality=85)
    product_image.thumbnail.save(
        f'thumb_{filename}',
        ContentFile(thumb_io.getvalue()),
        save=False
    )

    # ====== تصویر شاخص ======
    if product_image.is_primary:
        generate_featured(product_image, settings_obj)
    else:
        product_image.save()


def _generate_featured_windows(product_image, settings_obj):
    """
    تولید تصویر شاخص روی ویندوز با Pillow+arabic_reshaper
    """
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from django.core.files.base import ContentFile
    import arabic_reshaper
    from bidi.algorithm import get_display

    img_path = product_image.original.path
    img = Image.open(img_path)

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    filename = os.path.basename(product_image.original.name)
    product = product_image.product

    FEATURED_SIZE = settings_obj.featured_image_size or 1000
    INFO_BAR_HEIGHT = 120
    LOGO_MAX_HEIGHT = 60
    PADDING = 20

    # رنگ نوار
    try:
        primary_hex = settings_obj.info_bar_color or settings_obj.primary_color or '#C62828'
        bar_r = int(primary_hex[1:3], 16)
        bar_g = int(primary_hex[3:5], 16)
        bar_b = int(primary_hex[5:7], 16)
    except Exception:
        bar_r, bar_g, bar_b = 198, 40, 40
    BAR_COLOR = (bar_r, bar_g, bar_b)
    TEXT_COLOR = (255, 255, 255)

    # فونت
    FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts', 'vazirmatn')
    try:
        font_bold = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-Bold.ttf'), 28)
        font_regular = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-Regular.ttf'), 20)
        font_small = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-Regular.ttf'), 16)
    except Exception:
        try:
            font_bold = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-FD-Bold.ttf'), 28)
            font_regular = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-FD-Regular.ttf'), 20)
            font_small = ImageFont.truetype(os.path.join(FONT_DIR, 'Vazirmatn-FD-Regular.ttf'), 16)
        except Exception:
            font_bold = ImageFont.load_default()
            font_regular = ImageFont.load_default()
            font_small = ImageFont.load_default()

    canvas = Image.new('RGB', (FEATURED_SIZE, FEATURED_SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # تصویر فرش
    image_area_height = FEATURED_SIZE - INFO_BAR_HEIGHT
    img_copy = img.copy()
    img_copy.thumbnail((FEATURED_SIZE - PADDING * 2, image_area_height - PADDING * 2), Image.Resampling.LANCZOS)
    paste_x = (FEATURED_SIZE - img_copy.width) // 2
    paste_y = (image_area_height - img_copy.height) // 2
    canvas.paste(img_copy, (paste_x, paste_y))

    # لوگو
    try:
        if settings_obj.logo and os.path.isfile(settings_obj.logo.path):
            logo = Image.open(settings_obj.logo.path).convert('RGBA')
            logo.thumbnail((LOGO_MAX_HEIGHT * 3, LOGO_MAX_HEIGHT), Image.Resampling.LANCZOS)
            canvas.paste(logo, (FEATURED_SIZE - logo.width - PADDING, PADDING // 2), logo)
    except Exception:
        pass

    # نوار اطلاعات
    bar_y = FEATURED_SIZE - INFO_BAR_HEIGHT
    draw.rectangle([(0, bar_y), (FEATURED_SIZE, FEATURED_SIZE)], fill=BAR_COLOR)

    # متغیرهای قالب
    template_vars = {
        'name': product.name or '',
        'color': product.background_color.name if product.background_color else '',
        'comb': str(product.album.comb),
        'density': str(product.album.density) if product.album.density else '',
        'weave': product.weave_type.name if product.weave_type else '',
        'company': product.album.manufacturer.name,
        'yarn': product.album.get_yarn_type_display(),
        'mobile': settings_obj.mobile or '',
        'website': settings_obj.website_url or '',
        'site_name': settings_obj.site_name or '',
        'telegram': settings_obj.telegram_id or '',
    }

    line1_tpl = getattr(settings_obj, 'featured_line1_template', '') or 'نقشه {name} | رنگ {color} | {comb} شانه | تراکم {density}'
    line2_tpl = getattr(settings_obj, 'featured_line2_template', '') or '{company} | جنس نخ: {yarn} | {weave}'
    line3_tpl = getattr(settings_obj, 'featured_line3_template', '') or '{mobile}  |  {website}'

    def apply_template(tpl, vars_dict):
        try:
            result = tpl.format(**vars_dict)
        except (KeyError, ValueError):
            result = tpl
        result = result.replace('|  |', '|').replace('  |  ', ' | ')
        return result.strip(' |')

    def draw_rtl(text, font, y_pos):
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
        except Exception:
            bidi_text = text
        bbox = draw.textbbox((0, 0), bidi_text, font=font)
        tw = bbox[2] - bbox[0]
        x = (FEATURED_SIZE - tw) // 2
        draw.text((x, y_pos), bidi_text, fill=TEXT_COLOR, font=font)

    draw_rtl(apply_template(line1_tpl, template_vars), font_bold, bar_y + 12)
    draw_rtl(apply_template(line2_tpl, template_vars), font_regular, bar_y + 50)
    line3 = apply_template(line3_tpl, template_vars)
    if line3:
        draw_rtl(line3, font_small, bar_y + 85)

    featured_io = BytesIO()
    canvas.save(featured_io, format='JPEG', quality=92)
    product_image.featured_image.save(
        f'featured_{filename}',
        ContentFile(featured_io.getvalue()),
        save=False
    )
    product_image.save()
