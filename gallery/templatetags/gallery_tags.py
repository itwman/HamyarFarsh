from django import template

register = template.Library()


@register.filter
def format_duration(seconds):
    """تبدیل ثانیه به فرمت mm:ss"""
    if not seconds:
        return '--:--'
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f'{minutes}:{secs:02d}'


@register.filter
def format_size(bytes_val):
    """تبدیل بایت به فرمت خوانا"""
    if not bytes_val:
        return '--'
    if bytes_val < 1024:
        return f'{bytes_val} B'
    elif bytes_val < 1024 * 1024:
        return f'{bytes_val / 1024:.1f} KB'
    else:
        return f'{bytes_val / (1024 * 1024):.1f} MB'


@register.filter
def format_views(count):
    """تبدیل تعداد بازدید به فرمت خوانا"""
    if not count:
        return '۰'
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f'{count / 1000:.1f}K'
    else:
        return f'{count / 1000000:.1f}M'


@register.filter
def intcomma_fa(value):
    """جداکننده هزارگان با فارسی"""
    if not value:
        return '۰'
    try:
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return str(value)
