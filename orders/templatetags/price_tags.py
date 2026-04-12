"""فیلترهای قیمت برای نمایش مبالغ"""
from django import template

register = template.Library()


@register.filter(name='format_price')
def format_price(value):
    """فرمت کردن قیمت با جداکننده هزارگان و اضافه کردن 'تومان'"""
    if value is None:
        return '0 تومان'
    try:
        # تبدیل به int و فرمت با کاما
        return f"{int(value):,} تومان"
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='price_only')
def price_only(value):
    """فرمت کردن قیمت فقط با جداکننده هزارگان (بدون 'تومان')"""
    if value is None:
        return '0'
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='price_comma')
def price_comma(value):
    """جداکننده هزارگان بدون واحد (سازگاری با shop)"""
    if value is None or value == 0:
        return '-'
    try:
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='toman')
def format_toman(value):
    """فرمت قیمت به تومان با جداکننده هزارگان (سازگاری با shop)"""
    if value is None or value == 0:
        return '-'
    try:
        return f'{int(value):,} تومان'
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='star_range')
def star_range(value):
    """تبدیل عدد امتیاز به لیست ستاره‌ها (سازگاری با shop)"""
    try:
        val = float(value)
    except (ValueError, TypeError):
        val = 0
    full = int(val)
    half = 1 if val - full >= 0.5 else 0
    empty = 5 - full - half
    return {'full': range(full), 'half': half, 'empty': range(empty)}


@register.filter(name='mul')
def multiply(value, arg):
    """ضرب دو عدد (سازگاری با shop)"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
