"""
فاز 5: سیستم پردازش تصاویر همیار فرش

- فشرده‌سازی تصاویر (حداکثر 1MB با حفظ کیفیت)
- تولید تامبنیل (350×350 با فضای سفید)
- تولید تصویر شاخص 1000×1000 با لوگو و نوار اطلاعات فارسی
"""
import os
import io
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False

# Flag برای جلوگیری از loop سیگنال
_processing = False


def reshape_persian(text):
    """تبدیل متن فارسی برای نمایش صحیح در Pillow"""
    if not HAS_BIDI or not text:
        return text or ''
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except Exception:
        return str(text)


def get_vazirmatn_font(size=18, bold=False):
    """دریافت فونت Vazirmatn"""
    font_name = 'Vazirmatn-FD-Bold.ttf' if bold else 'Vazirmatn-FD-Regular.ttf'
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'vazirmatn', font_name)
    try:
        return ImageFont.truetype(font_path, size)
    except (OSError, IOError):
        alt_name = 'Vazirmatn-Bold.ttf' if bold else 'Vazirmatn-Regular.ttf'
        alt_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'vazirmatn', alt_name)
        try:
            return ImageFont.truetype(alt_path, size)
        except (OSError, IOError):
            return ImageFont.load_default()


def _to_rgb(img):
    """تبدیل تصویر به RGB"""
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img


def hex_to_rgb(hex_color):
    """تبدیل رنگ HEX به RGB"""
    hex_color = hex_color.lstrip('#')
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (198, 40, 40)


# ============================================================
# 5.1: فشرده‌سازی تصاویر
# ============================================================

def compress_image(image_file, max_size_mb=None, max_dimension=2500):
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

    while max(img.size) > 800:
        new_w = int(img.size[0] * 0.8)
        new_h = int(img.size[1] * 0.8)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=75, optimize=True)
        if buffer.tell() <= max_bytes:
            buffer.seek(0)
            return ContentFile(buffer.read()), img.size

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=60, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read()), img.size


# ============================================================
# 5.2: تولید تامبنیل
# ============================================================

def generate_thumbnail(image_file, size=None):
    if size is None:
        from settings_app.models import SiteSettings
        ss = SiteSettings.get_settings()
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
    offset_x = (size[0] - new_w) // 2
    offset_y = (size[1] - new_h) // 2
    thumb.paste(img_resized, (offset_x, offset_y))

    buffer = io.BytesIO()
    thumb.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read())


# ============================================================
# 5.3: تولید تصویر شاخص 1000×1000
# ============================================================

def generate_featured_image(image_file, product, size=None):
    from settings_app.models import SiteSettings
    ss = SiteSettings.get_settings()

    if size is None:
        dim = ss.featured_image_size or 1000
        size = (dim, dim)

    W, H = size
    bar_color = hex_to_rgb(ss.info_bar_color or '#C62828')
    bar_color_dark = tuple(max(0, c - 40) for c in bar_color)

    canvas = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    logo_area_h = 60
    info_bar_h = 120
    carpet_area_h = H - logo_area_h - info_bar_h

    # --- بالا: لوگو ---
    draw.rectangle([(0, 0), (W, logo_area_h)], fill=(250, 250, 250))
    if ss.logo:
        try:
            logo_img = Image.open(ss.logo.path)
            logo_h = logo_area_h - 16
            logo_ratio = logo_img.size[0] / logo_img.size[1]
            logo_w = int(logo_h * logo_ratio)
            logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
            if logo_img.mode == 'RGBA':
                canvas.paste(logo_img, (W - logo_w - 16, 8), logo_img)
            else:
                canvas.paste(logo_img, (W - logo_w - 16, 8))
        except Exception:
            pass

    font_site = get_vazirmatn_font(20, bold=True)
    site_text = reshape_persian(ss.site_name or 'همیار فرش')
    draw.text((16, logo_area_h // 2), site_text, fill=bar_color, font=font_site, anchor='lm')

    # --- وسط: تصویر فرش ---
    img = _to_rgb(Image.open(image_file))
    carpet_area_w = W - 20
    img_ratio = img.size[0] / img.size[1]
    area_ratio = carpet_area_w / carpet_area_h
    if img_ratio > area_ratio:
        new_w = carpet_area_w
        new_h = int(carpet_area_w / img_ratio)
    else:
        new_h = carpet_area_h
        new_w = int(carpet_area_h * img_ratio)

    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    offset_x = (W - new_w) // 2
    offset_y = logo_area_h + (carpet_area_h - new_h) // 2
    canvas.paste(img_resized, (offset_x, offset_y))

    # --- پایین: نوار اطلاعات ---
    bar_top = H - info_bar_h
    draw.rectangle([(0, bar_top), (W, H)], fill=bar_color)
    draw.rectangle([(0, bar_top), (W, bar_top + 3)], fill=bar_color_dark)

    font_title = get_vazirmatn_font(22, bold=True)
    font_info = get_vazirmatn_font(16, bold=False)
    font_contact = get_vazirmatn_font(14, bold=False)
    text_color = (255, 255, 255)

    # ردیف 1: نام نقشه + رنگ + شانه
    y1 = bar_top + 12
    info_parts = [f'نقشه {product.name}']
    if product.background_color:
        info_parts.append(f'رنگ {product.background_color.name}')
    info_parts.append(f'{product.comb} شانه')
    if product.density:
        info_parts.append(f'تراکم {product.density}')
    draw.text((W // 2, y1), reshape_persian(' | '.join(info_parts)), fill=text_color, font=font_title, anchor='mt')

    # ردیف 2: شرکت و جنس نخ
    y2 = y1 + 32
    detail_parts = [product.manufacturer.name, f'جنس نخ: {product.yarn_type}']
    if product.weave_type:
        detail_parts.append(product.weave_type.name)
    draw.text((W // 2, y2), reshape_persian(' | '.join(detail_parts)), fill=text_color, font=font_info, anchor='mt')

    # ردیف 3: تماس
    y3 = y2 + 28
    contact_parts = []
    if ss.mobile:
        contact_parts.append(ss.mobile)
    if ss.whatsapp:
        contact_parts.append(f'واتساپ: {ss.whatsapp}')
    if ss.telegram_id:
        contact_parts.append(f'تلگرام: @{ss.telegram_id}')
    if contact_parts:
        draw.text((W // 2, y3), reshape_persian(' | '.join(contact_parts)), fill=text_color, font=font_contact, anchor='mt')

    # ردیف 4: سایت
    y4 = y3 + 24
    if ss.website_url:
        draw.text((W // 2, y4), reshape_persian(ss.website_url), fill=text_color, font=font_contact, anchor='mt')

    buffer = io.BytesIO()
    canvas.save(buffer, format='JPEG', quality=90, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read())


# ============================================================
# 5.4: پردازش کامل تصویر محصول
# ============================================================

def process_product_image(product_image_obj):
    """پردازش کامل: فشرده‌سازی + تامبنیل + تصویر شاخص"""
    global _processing
    if _processing:
        return
    if not product_image_obj.original:
        return

    _processing = True
    try:
        original_path = product_image_obj.original.path
        product = product_image_obj.product
        slug = product.slug or f'product-{product.pk}'

        # 1. فشرده‌سازی
        try:
            compressed, dimensions = compress_image(original_path)
            fname = f'{slug}-{product_image_obj.pk or "new"}.jpg'
            product_image_obj.original.save(fname, compressed, save=False)
        except Exception as e:
            print(f'[HF] Compress error: {e}')

        # 2. تامبنیل
        try:
            thumb_content = generate_thumbnail(original_path)
            thumb_fname = f'{slug}-{product_image_obj.pk or "new"}-thumb.jpg'
            product_image_obj.thumbnail.save(thumb_fname, thumb_content, save=False)
        except Exception as e:
            print(f'[HF] Thumbnail error: {e}')

        # 3. تصویر شاخص (فقط primary)
        if product_image_obj.is_primary:
            try:
                featured_content = generate_featured_image(original_path, product)
                feat_fname = f'{slug}-featured.jpg'
                product_image_obj.featured_image.save(feat_fname, featured_content, save=False)
            except Exception as e:
                print(f'[HF] Featured error: {e}')

        # ذخیره بدون trigger سیگنال (با flag _processing)
        product_image_obj.save()

    finally:
        _processing = False
