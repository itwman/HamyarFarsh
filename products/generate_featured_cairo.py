"""
اسکریپت مستقل برای ساخت تصویر شاخص با cairo+pango
اجرا با python3 سیستمی (نه venv)
"""
import sys
import json
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image
import io

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    try:
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    except:
        return (0.78, 0.16, 0.16)

def draw_persian_text(ctx, text, font_name, font_size, bold, y, width, color):
    """رسم متن فارسی با pango - وسط‌چین"""
    layout = PangoCairo.create_layout(ctx)
    layout.set_text(text, -1)
    weight = 'Bold' if bold else 'Regular'
    font_desc = Pango.FontDescription(f'Vazirmatn {weight} {font_size}')
    layout.set_font_description(font_desc)
    layout.set_alignment(Pango.Alignment.CENTER)
    layout.set_width(width * Pango.SCALE)
    ctx.set_source_rgb(*color)
    ctx.move_to(0, y)
    PangoCairo.show_layout(ctx, layout)
    # ارتفاع متن رو برگردون
    _, logical = layout.get_extents()
    return logical.height / Pango.SCALE

def generate(params, image_path, output_path):
    W = params.get('width', 1000)
    H = params.get('height', 1000)
    bar_color_hex = params.get('bar_color', '#C62828')
    bar_color = hex_to_rgb(bar_color_hex)
    bar_color_dark = tuple(max(0, c - 0.15) for c in bar_color)
    text_color = (1.0, 1.0, 1.0)

    logo_area_h = 60
    info_bar_h = 120
    carpet_area_h = H - logo_area_h - info_bar_h

    # ساخت surface
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surface)

    # --- پس‌زمینه سفید ---
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # --- بالا: نوار لوگو ---
    ctx.set_source_rgb(0.98, 0.98, 0.98)
    ctx.rectangle(0, 0, W, logo_area_h)
    ctx.fill()

    # نام سایت
    site_name = params.get('site_name', 'همیار فرش')
    draw_persian_text(ctx, site_name, 'Vazirmatn', 20, True,
                     logo_area_h // 2 - 14, W, bar_color)

    # --- وسط: تصویر فرش ---
    try:
        carpet_img = Image.open(image_path).convert('RGB')
        img_ratio = carpet_img.width / carpet_img.height
        area_ratio = (W - 20) / carpet_area_h
        if img_ratio > area_ratio:
            new_w = W - 20
            new_h = int((W - 20) / img_ratio)
        else:
            new_h = carpet_area_h
            new_w = int(carpet_area_h * img_ratio)

        carpet_img = carpet_img.resize((new_w, new_h), Image.LANCZOS)
        offset_x = (W - new_w) // 2
        offset_y = logo_area_h + (carpet_area_h - new_h) // 2

        # تبدیل PIL به cairo surface
        carpet_data = carpet_img.tobytes('raw', 'BGRX')
        carpet_surface = cairo.ImageSurface.create_for_data(
            bytearray(carpet_data), cairo.FORMAT_RGB24, new_w, new_h
        )
        ctx.set_source_surface(carpet_surface, offset_x, offset_y)
        ctx.paint()
    except Exception as e:
        print(f'Error loading carpet image: {e}', file=sys.stderr)

    # --- پایین: نوار اطلاعات ---
    bar_top = H - info_bar_h
    ctx.set_source_rgb(*bar_color)
    ctx.rectangle(0, bar_top, W, info_bar_h)
    ctx.fill()
    ctx.set_source_rgb(*bar_color_dark)
    ctx.rectangle(0, bar_top, W, 3)
    ctx.fill()

    # ردیف ۱
    line1 = params.get('line1', '')
    if line1:
        draw_persian_text(ctx, line1, 'Vazirmatn', 22, True,
                         bar_top + 10, W, text_color)

    # ردیف ۲
    line2 = params.get('line2', '')
    if line2:
        draw_persian_text(ctx, line2, 'Vazirmatn', 16, False,
                         bar_top + 42, W, text_color)

    # ردیف ۳
    line3 = params.get('line3', '')
    if line3:
        draw_persian_text(ctx, line3, 'Vazirmatn', 14, False,
                         bar_top + 70, W, text_color)

    # ردیف ۴
    line4 = params.get('line4', '')
    if line4:
        draw_persian_text(ctx, line4, 'Vazirmatn', 13, False,
                         bar_top + 95, W, text_color)

    # ذخیره PNG موقت
    tmp_png = output_path + '.tmp.png'
    surface.write_to_png(tmp_png)

    # تبدیل به JPEG با PIL
    img = Image.open(tmp_png).convert('RGB')
    img.save(output_path, 'JPEG', quality=90, optimize=True)

    import os
    os.remove(tmp_png)
    print(f'OK:{output_path}')

if __name__ == '__main__':
    # params از stdin میاد
    params = json.loads(sys.stdin.read())
    image_path = params.pop('image_path')
    output_path = params.pop('output_path')
    generate(params, image_path, output_path)
