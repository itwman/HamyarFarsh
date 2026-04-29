"""تمپلیت‌تگ‌های تاریخ شمسی - با پشتیبانی locale فارسی"""
from django import template
import jdatetime

register = template.Library()

# تنظیم locale فارسی برای jdatetime تا نام ماه‌ها فارسی نمایش داده شود
# (به جای Ordibehesht → اردیبهشت)
try:
    jdatetime.set_locale('fa_IR')
except Exception:
    pass

# نقشه نام ماه‌های انگلیسی به فارسی (fallback اگر locale کار نکرد)
PERSIAN_MONTHS = {
    'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
    'Tir': 'تیر', 'Mordad': 'مرداد', 'Shahrivar': 'شهریور',
    'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
    'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند',
}

PERSIAN_WEEKDAYS = {
    'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه',
    'Tuesday': 'سه‌شنبه', 'Wednesday': 'چهارشنبه', 'Thursday': 'پنج‌شنبه',
    'Friday': 'جمعه',
    # فرم کوتاه‌شده jdatetime
    'Sat': 'شنبه', 'Sun': 'یکشنبه', 'Mon': 'دوشنبه',
    'Tue': 'سه‌شنبه', 'Wed': 'چهارشنبه', 'Thu': 'پنج‌شنبه', 'Fri': 'جمعه',
}

ENGLISH_TO_PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def _to_persian(text, persian_digits=True):
    """جایگزینی نام ماه/روز انگلیسی با فارسی + ارقام فارسی"""
    if not text:
        return text
    # ماه‌ها
    for en, fa in PERSIAN_MONTHS.items():
        text = text.replace(en, fa)
    # روزهای هفته
    for en, fa in PERSIAN_WEEKDAYS.items():
        text = text.replace(en, fa)
    # ارقام
    if persian_digits:
        text = text.translate(ENGLISH_TO_PERSIAN_DIGITS)
    return text


@register.filter(name='jalali')
def to_jalali(value, fmt='%Y/%m/%d'):
    """تبدیل تاریخ میلادی به شمسی"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return _to_persian(jdate.strftime(fmt))
    except (ValueError, AttributeError):
        return str(value)


@register.filter(name='jalali_full')
def to_jalali_full(value):
    """تبدیل به تاریخ شمسی کامل: ۱۵ فروردین ۱۴۰۵"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return _to_persian(jdate.strftime('%d %B %Y'))
    except (ValueError, AttributeError):
        return str(value)


@register.filter(name='jalali_datetime')
def to_jalali_datetime(value):
    """تبدیل به تاریخ و ساعت شمسی"""
    if value is None:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        return _to_persian(jdate.strftime('%Y/%m/%d - %H:%M'))
    except (ValueError, AttributeError):
        return str(value)


@register.simple_tag
def jalali_now(fmt='%Y/%m/%d'):
    """تاریخ شمسی الان (با نام ماه/روز فارسی و ارقام فارسی)"""
    return _to_persian(jdatetime.datetime.now().strftime(fmt))

