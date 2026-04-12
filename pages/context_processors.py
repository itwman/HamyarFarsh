"""Context processor برای صفحات فوتر و هدر"""
from .models import Page


def cms_pages(request):
    """لینک صفحات ایستا برای هدر و فوتر"""
    return {
        'footer_pages': Page.objects.filter(
            status='published', show_in_footer=True
        ).order_by('menu_order').values('title', 'slug', 'page_type')[:10],
        'header_pages': Page.objects.filter(
            status='published', show_in_header=True
        ).order_by('menu_order').values('title', 'slug', 'page_type')[:8],
    }
