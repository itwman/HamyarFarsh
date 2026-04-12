"""Context processor برای شمارنده علاقه‌مندی و مقایسه"""
from .models import WishlistItem


def wishlist_compare_context(request):
    """شمارنده‌های navbar"""
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()

    compare_count = len(request.session.get('compare_products', []))

    return {
        'wishlist_count': wishlist_count,
        'compare_count': compare_count,
    }
