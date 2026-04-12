"""
فاز 18: لیست علاقه‌مندی و مقایسه محصولات
- Wishlist: ذخیره محصولات مورد علاقه (DB برای لاگین‌شده)
- مقایسه: session-based (حداکثر 4 محصول)
- محصولات اخیراً بازدیدشده: session/cookie
"""
from django.db import models
from django.conf import settings


class WishlistItem(models.Model):
    """آیتم لیست علاقه‌مندی"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='wishlist_items', verbose_name='کاربر')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,
                                related_name='wishlisted_by', verbose_name='محصول')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'لیست علاقه‌مندی‌ها'
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user} ❤ {self.product.name}'
