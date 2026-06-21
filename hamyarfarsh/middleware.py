"""
Middleware چندزبانه همیار فرش
زبان را از روی ساب‌دامین تشخیص و فعال می‌کند.

نمونه‌ها:
    fa.hamyarfarsh.ir / www.hamyarfarsh.ir / hamyarfarsh.ir  -> fa (پیش‌فرض)
    en.hamyarfarsh.ir -> en
    ar.hamyarfarsh.ir -> ar
    ru / es / fr / de / ur / hi نیز به همین ترتیب.

اگر ساب‌دامین با هیچ زبان تعریف‌شده‌ای در LANGUAGES مطابقت نداشته باشد،
زبان پیش‌فرض (LANGUAGE_CODE) فعال می‌شود.
"""
from django.conf import settings
from django.utils import translation
from django.utils.cache import patch_vary_headers


class SubdomainLocaleMiddleware:
    """فعال‌سازی زبان بر اساس ساب‌دامین درخواست."""

    def __init__(self, get_response):
        self.get_response = get_response
        # مجموعه‌ی کدهای زبان پشتیبانی‌شده از روی settings.LANGUAGES
        self.supported = {code for code, _name in settings.LANGUAGES}

    def _language_from_host(self, request):
        host = request.get_host().split(':')[0].lower()
        label = host.split('.')[0]
        if label in self.supported:
            return label
        return settings.LANGUAGE_CODE

    def __call__(self, request):
        language = self._language_from_host(request)
        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        translation.deactivate()
        patch_vary_headers(response, ('Accept-Language',))
        response.setdefault('Content-Language', language)
        return response
