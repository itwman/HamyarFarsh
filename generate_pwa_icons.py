"""
تولید آیکون‌های PWA از لوگو سایت
اجرا: python generate_pwa_icons.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'hamyarfarsh.settings'

import django
django.setup()

from PIL import Image, ImageDraw, ImageFont

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images', 'pwa')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# سعی کن لوگو سایت رو استفاده کنی
try:
    from settings_app.models import SiteSettings
    ss = SiteSettings.get_solo()
    if ss.logo and os.path.exists(ss.logo.path):
        logo = Image.open(ss.logo.path).convert('RGBA')
        print(f"لوگو پیدا شد: {ss.logo.path}")
    else:
        raise Exception("No logo")
except Exception:
    # آیکون placeholder تولید کن
    logo = None
    print("لوگو پیدا نشد. آیکون placeholder تولید می‌شود.")

for size in SIZES:
    img = Image.new('RGBA', (size, size), (198, 40, 40, 255))  # رنگ اصلی #C62828

    if logo:
        # لوگو رو resize و وسط بذار
        padding = int(size * 0.15)
        inner = size - padding * 2
        resized = logo.copy()
        resized.thumbnail((inner, inner), Image.LANCZOS)
        x = (size - resized.width) // 2
        y = (size - resized.height) // 2
        img.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)
    else:
        # متن فارسی (اگه فونت نبود، فقط رنگ)
        draw = ImageDraw.Draw(img)
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'vazirmatn', 'Vazirmatn-Bold.ttf')
            font_size = int(size * 0.3)
            font = ImageFont.truetype(font_path, font_size)
            text = 'هـف'
        except Exception:
            font = ImageFont.load_default()
            text = 'HF'

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (size - tw) // 2
        y = (size - th) // 2
        draw.text((x, y), text, fill='white', font=font)

    # ذخیره PNG
    path = os.path.join(OUTPUT_DIR, f'icon-{size}.png')
    img.save(path, 'PNG')
    print(f"  ✓ {path} ({size}x{size})")

print(f"\nتمام آیکون‌ها در {OUTPUT_DIR} تولید شد.")
