"""تمپلیت‌تگ‌های تاریخ شمسی"""
from django import template
import jdatetime

register = template.Library()


@register.filter(name='jalali')
def to_jalali(value, fmt='%Y/%m/%d'):
    """تبدیل تاریخ میلادی به شمسی"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return jdate.strftime(fmt)
    except (ValueError, AttributeError):
        return str(value)


@register.filter(name='jalali_full')
def to_jalali_full(value):
    """تبدیل به تاریخ شمسی کامل: 15 فروردین 1405"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return jdate.strftime('%d %B %Y')
    except (ValueError, AttributeError):
        return str(value)


@register.filter(name='jalali_datetime')
def to_jalali_datetime(value):
    """تبدیل به تاریخ و ساعت شمسی"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return jdate.strftime('%Y/%m/%d - %H:%M')
    except (ValueError, AttributeError):
        return str(value)


@register.simple_tag
def jalali_now(fmt='%Y/%m/%d'):
    """تاریخ شمسی الان"""
    return jdatetime.datetime.now().strftime(fmt)
