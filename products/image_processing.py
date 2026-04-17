"""
فاز 5: سیستم پردازش تصاویر همیار فرش
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
        if img.mode == 'P': img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        return background
    elif img.mode != 'RGB': return img.convert('RGB')
    return img

def compress_image(image_file, max_size_mb=None, max_dimension=2500):
    if max_size_mb is None: max_size_mb = getattr(settings, 'MAX_IMAGE_SIZE_MB', 1)
    max_bytes = int(max_size_mb * 1024 * 1024)
    img = _to_rgb(Image.open(image_file))
    if max(img.size) > max_dimension: img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
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
    if size is None:
        from settings_app.models import SiteSettings
        ss = SiteSettings.get_solo()
        size = (ss.thumbnail_width, ss.thumbnail_height)
    img = _to_rgb(Image.open(image_file))
    thumb = Image.new('RGB', size, (255, 255, 255))
    img_ratio = img.size[0] / img.size[1]
    thumb_ratio = size[0] / size[1]
    if img_ratio > thumb_ratio:
        new_w = size[0]; new_h = int(size[0] / img_ratio)
    else:
        new_h = size[1]; new_w = int(size[1] * img_ratio)
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    thumb.paste(img_resized, ((size[0]-new_w)//2, (size[1]-new_h)//2))
    buffer = io.BytesIO()
    thumb.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    return ContentFile(buffer.read())

def generate_featured_image(image_file, product, size=None):
    from settings_app.models import SiteSettings
    ss = SiteSettings.get_solo()
    if size is None:
        dim = ss.featured_image_size or 1000
        size = (dim, dim)
    W, H = size
    info_parts = [f'نقشه {product.name}']
    if product.background_color: info_parts.append(f'رنگ {product.background_color.name}')
    info_parts.append(f'{product.comb} شانه')
    if product.density: info_parts.append(f'تراکم {product.density}')
    detail_parts = [product.manufacturer.name, f'جنس نخ: {product.yarn_type}']
    if product.weave_type: detail_parts.append(product.weave_type.name)
    contact_parts = []
    if ss.mobile: contact_parts.append(ss.mobile)
    if ss.whatsapp: contact_parts.append(f'واتساپ: {ss.whatsapp}')
    if ss.telegram_id: contact_parts.append(f'تلگرام: @{ss.telegram_id}')
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_output = tmp.name
    try:
        params = {
            'width': W, 'height': H,
            'bar_color': ss.info_bar_color or '#C62828',
            'site_name': ss.site_name or 'همیار فرش',
            'line1': ' | '.join(info_parts),
            'line2': ' | '.join(detail_parts),
            'line3': ' | '.join(contact_parts),
            'line4': ss.website_url or '',
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
        if os.path.exists(tmp_output): os.remove(tmp_output)

def process_product_image(product_image_obj):
    global _processing
    if _processing or not product_image_obj.original: return
    _processing = True
    try:
        original_path = product_image_obj.original.path
        product = product_image_obj.product
        slug = product.slug or f'product-{product.pk}'
        try:
            compressed, _ = compress_image(original_path)
            product_image_obj.original.save(f'{slug}-{product_image_obj.pk or "new"}.jpg', compressed, save=False)
        except Exception as e: print(f'[HF] Compress error: {e}')
        try:
            thumb = generate_thumbnail(original_path)
            product_image_obj.thumbnail.save(f'{slug}-{product_image_obj.pk or "new"}-thumb.jpg', thumb, save=False)
        except Exception as e: print(f'[HF] Thumbnail error: {e}')
        if product_image_obj.is_primary:
            try:
                featured = generate_featured_image(original_path, product)
                product_image_obj.featured_image.save(f'{slug}-featured.jpg', featured, save=False)
            except Exception as e: print(f'[HF] Featured error: {e}')
        product_image_obj.save()
    finally:
        _processing = False
