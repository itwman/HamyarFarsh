"""Context processor برای فهرست‌ها و ویجت‌های فوتر"""
from .models import MenuItem, FooterWidget


def appearance_context(request):
    """منوهای هدر/فوتر + ویجت‌های فوتر"""
    header_menu = MenuItem.objects.filter(
        is_active=True, position__in=['header', 'both'], parent__isnull=True
    ).prefetch_related('children').order_by('order')

    footer_widgets = FooterWidget.objects.filter(is_active=True).order_by('column', 'order')

    # گروه‌بندی ویجت‌ها بر اساس ستون
    widget_columns = {}
    for w in footer_widgets:
        col = w.column
        if col not in widget_columns:
            widget_columns[col] = []
        widget_columns[col].append(w)

    return {
        'header_menu_items': header_menu,
        'footer_widget_columns': widget_columns,
    }
