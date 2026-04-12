from .models import SiteSettings


def site_settings(request):
    """تزریق تنظیمات سایت به تمام قالب‌ها"""
    return {
        'site_settings': SiteSettings.get_solo(),
        'ss': SiteSettings.get_solo(),  # میانبر برای استفاده در تمپلیت‌ها
    }
