"""
فاز 5: سیستم پردازش تصاویر همیار فرش
- فشرده‌سازی خودکار (حداکثر 1MB)
- تولید تامبنیل
- تولید تصویر شاخص 1000×1000
- حذف فایل‌های یتیم (orphan) بعد از فشرده‌سازی
"""
import os, io, json, subprocess, tempfile
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile

_processing = False
CAIRO_SCRIPT = os.path.join(settings.BASE_DIR, 'products', 'generate_featured_cairo.py')


def _to_rgb(img):
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img


def _safe_delete(path):
    """حذف امن فایل از دیسک"""
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def compress_image(image_file, max_size_mb=None, max_dimension=2500):
    """
    فشرده‌سازی تصویر با حفظ حداکثری کیفیت.
    شروع از quality=92 و کاهش تا زیر حد مجاز بشه.
    """
    if max_size_mb is None:
        max_size_mb = getattr(settings, 'MAX_IMAGE_SIZE_MB', 1)
    max_bytes = int(max_size_mb * 1024 * 1024)
    img = _to_rgb(Image.open(image_file))
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    quality = 92
    while quality >= 30:
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        if buffer.tell() <= max_bytes:
            buffer.seek(0)
            return ContentFile(buffer.read()), img.size
        quality -= 5
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=60, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read()), img.size


def generate_thumbnail(image_file, size=None):
    """تولید تامبنیل با حفظ نسبت تصویر"""
    if size is None:
        from settings_app.models import SiteSettings
        ss = SiteSettings.get_solo()
        size = (ss.thumbnail_width, ss.thumbnail_height)
    img = _to_rgb(Image.open(image_file))
    thumb = Image.new('RGB', size, (255, 255, 255))
    img_ratio = img.size[0] / img.size[1]
    thumb_ratio = size[0] / size[1]
    if img_ratio > thumb_ratio:
        new_w = size[0]
        new_h = int(size[0] / img_ratio)
    else:
        new_h = size[1]
        new_w = int(size[1] * img_ratio)
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    thumb.paste(img_resized, ((size[0] - new_w) // 2, (size[1] - new_h) // 2))
    buffer = io.BytesIO()
    thumb.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read())


def generate_featured_image(image_file, product, size=None):
    """تولید تصویر شاخص 1000x1000 با نوار اطلاعات (Cairo روی لینوکس)"""
    from settings_app.models import SiteSettings
    ss = SiteSettings.get_solo()
    if size is None:
        dim = ss.featured_image_size or 1000
        size = (dim, dim)
    W, H = size

    # متغیرهای قالب - همسان با نسخه ویندوز
    template_vars = {
        'name': product.name or '',
        'color': product.background_color.name if product.background_color else '',
        'comb': str(product.album.comb),
        'density': str(product.album.density) if product.album.density else '',
        'design': product.design_type_display if hasattr(product, 'design_type_display') else '',
        'weave': product.weave_type.name if product.weave_type else '',
        'feature': product.feature.name if product.feature else '',
        'company': product.album.manufacturer.name,
        'album': product.album.name,
        'yarn': product.album.get_yarn_type_display(),
        'mobile': ss.mobile or '',
        'phone': ss.phone or '',
        'website': ss.website_url or '',
        'site_name': ss.site_name or '',
        'telegram': ss.telegram_id or '',
        'instagram': ss.instagram_id or '',
    }

    def apply_template(tpl, vars_dict):
        """جایگزینی متغیرها در قالب و پاکسازی جداکننده‌های خالی"""
        try:
            result = tpl.format(**vars_dict)
        except (KeyError, ValueError):
            result = tpl
        # پاکسازی جداکننده‌های تکراری و خالی
        result = result.replace('|  |', '|').replace('  |  ', ' | ')
        result = result.replace('•  •', '•').replace('  •  ', ' • ')
        return result.strip(' |•')

    # خوندن templates از تنظیمات
    line1_tpl = (getattr(ss, 'featured_line1_template', '') or
                 'نقشه {name} | رنگ {color} | {comb} شانه | تراکم {density}')
    line2_tpl = (getattr(ss, 'featured_line2_template', '') or
                 '{company} | جنس نخ: {yarn} | {weave}')
    line3_tpl = (getattr(ss, 'featured_line3_template', '') or
                 '{mobile}  •  {website}')

    # پر کردن قالب‌ها
    line1 = apply_template(line1_tpl, template_vars)
    line2 = apply_template(line2_tpl, template_vars)
    line3 = apply_template(line3_tpl, template_vars)

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_output = tmp.name
    try:
        params = {
            'width': W, 'height': H,
            'bar_color': ss.info_bar_color or '#C62828',
            'site_name': ss.site_name or 'همیار فرش',
            'line1': line1,
            'line2': line2,
            'line3': line3,
            'line4': '',  # دیگر استفاده نمی‌شود - همه چیز در line3 است
            'image_path': str(image_file),
            'output_path': tmp_output,
        }
        result = subprocess.run(
            ['/usr/bin/python3', CAIRO_SCRIPT],
            input=json.dumps(params, ensure_ascii=False),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise Exception(f'Cairo error: {result.stderr}')
        with open(tmp_output, 'rb') as f:
            return ContentFile(f.read())
    finally:
        if os.path.exists(tmp_output):
            os.remove(tmp_output)


def process_product_image(product_image_obj):
    """
    پردازش کامل تصویر محصول:
    1. فشرده‌سازی تصویر اصلی (حفظ کیفیت، کاهش حجم)
    2. تولید تامبنیل
    3. تولید تصویر شاخص (فقط is_primary)
    4. حذف فایل قدیمی از دیسک (جلوگیری از orphan files)
    """
    global _processing
    if _processing or not product_image_obj.original:
        return
    _processing = True
    try:
        original_path = product_image_obj.original.path
        product = product_image_obj.product
        slug = product.slug or f'product-{product.pk}'
        img_id = product_image_obj.pk or 'new'

        # ===== 1. فشرده‌سازی اصلی =====
        try:
            old_original_path = original_path  # مسیر فایل فعلی قبل از فشرده‌سازی
            compressed, _ = compress_image(original_path)
            product_image_obj.original.save(
                f'{slug}-{img_id}.jpg', compressed, save=False
            )
            # حذف فایل قدیمی اگه نام فایل عوض شده (جلوگیری از orphan)
            new_path = product_image_obj.original.path
            if old_original_path != new_path:
                _safe_delete(old_original_path)
        except Exception as e:
            print(f'[HF] Compress error: {e}')

        # ===== 2. تولید تامبنیل =====
        try:
            # تامبنیل رو از فایل فشرده‌شده جدید بساز
            current_path = product_image_obj.original.path
            old_thumb_path = None
            if product_image_obj.thumbnail:
                try:
                    old_thumb_path = product_image_obj.thumbnail.path
                except Exception:
                    pass
            thumb = generate_thumbnail(current_path)
            product_image_obj.thumbnail.save(
                f'{slug}-{img_id}-thumb.jpg', thumb, save=False
            )
            # حذف تامبنیل قدیمی
            if old_thumb_path:
                new_thumb = product_image_obj.thumbnail.path
                if old_thumb_path != new_thumb:
                    _safe_delete(old_thumb_path)
        except Exception as e:
            print(f'[HF] Thumbnail error: {e}')

        # ===== 3. تصویر شاخص (فقط is_primary) =====
        if product_image_obj.is_primary:
            try:
                current_path = product_image_obj.original.path
                old_featured_path = None
                if product_image_obj.featured_image:
                    try:
                        old_featured_path = product_image_obj.featured_image.path
                    except Exception:
                        pass
                featured = generate_featured_image(current_path, product)
                product_image_obj.featured_image.save(
                    f'{slug}-featured.jpg', featured, save=False
                )
                if old_featured_path:
                    new_featured = product_image_obj.featured_image.path
                    if old_featured_path != new_featured:
                        _safe_delete(old_featured_path)
            except Exception as e:
                print(f'[HF] Featured error: {e}')

        product_image_obj.save()
    finally:
        _processing = False


def cleanup_orphan_files():
    """
    پاکسازی فایل‌های یتیم (orphan) در پوشه media.
    فایل‌هایی که روی دیسک هستن ولی هیچ رکوردی در DB بهشون اشاره نمی‌کنه.
    شامل تصاویر و ویدیوها.
    """
    from products.models import ProductImage, ProductVideo
    import os

    media_root = settings.MEDIA_ROOT

    # === فایل‌های تصویری در DB ===
    image_db_files = set()
    for img in ProductImage.objects.all():
        if img.original:
            image_db_files.add(os.path.basename(img.original.name))
        if img.thumbnail:
            image_db_files.add(os.path.basename(img.thumbnail.name))
        if img.featured_image:
            image_db_files.add(os.path.basename(img.featured_image.name))

    # === فایل‌های ویدیویی در DB ===
    video_db_files = set()
    for vid in ProductVideo.objects.all():
        if vid.original_file:
            video_db_files.add(os.path.basename(vid.original_file.name))
        if vid.video_720p:
            video_db_files.add(os.path.basename(vid.video_720p.name))
        if vid.video_480p:
            video_db_files.add(os.path.basename(vid.video_480p.name))
        if vid.thumbnail:
            video_db_files.add(os.path.basename(vid.thumbnail.name))

    # ترکیب همه
    all_db_files = image_db_files | video_db_files

    # پوشه‌هایی که باید بررسی بشن
    folders = [
        'products/originals',
        'products/thumbnails',
        'products/featured',
        'products/videos/originals',
        'products/videos/720p',
        'products/videos/480p',
        'products/videos/thumbnails',
    ]

    orphans = []
    for folder in folders:
        folder_path = os.path.join(media_root, folder)
        if not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if filename not in all_db_files:
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    orphans.append({
                        'path': filepath,
                        'size': os.path.getsize(filepath),
                        'folder': folder,
                        'filename': filename,
                    })

    return orphans


def delete_orphan_files():
    """حذف فایل‌های یتیم و برگرداندن فضای آزادشده"""
    orphans = cleanup_orphan_files()
    freed = 0
    deleted = 0
    for orphan in orphans:
        try:
            os.remove(orphan['path'])
            freed += orphan['size']
            deleted += 1
        except OSError:
            pass
    return deleted, freed
