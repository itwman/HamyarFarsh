"""
فاز 17: سیستم کوپن تخفیف
- کوپن درصدی/مبلغی با سقف
- محدودیت تعداد استفاده (کلی و به ازای کاربر)
- تاریخ انقضا + حداقل مبلغ سفارش
- محدودیت به محصولات/دسته‌بندی خاص (اختیاری)
- لاگ استفاده
"""
import string
import random
import jdatetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Coupon(models.Model):
    """کوپن تخفیف"""

    class CouponType(models.TextChoices):
        PERCENT = 'percent', 'درصدی'
        FIXED = 'fixed', 'مبلغی (تومان)'

    # کد تخفیف
    code = models.CharField(max_length=30, unique=True, verbose_name='کد تخفیف',
                            help_text='حروف انگلیسی و اعداد. مثال: SUMMER1405')

    # نوع و مقدار
    coupon_type = models.CharField(max_length=10, choices=CouponType.choices, verbose_name='نوع تخفیف')
    amount = models.BigIntegerField(verbose_name='مقدار تخفیف',
                                     help_text='درصدی: عدد 1-100 / مبلغی: مبلغ به تومان',
                                     validators=[MinValueValidator(1)])
    max_discount = models.BigIntegerField(null=True, blank=True, verbose_name='سقف تخفیف (تومان)',
                                           help_text='فقط برای نوع درصدی. خالی = بدون سقف')

    # شرایط استفاده
    min_order_amount = models.BigIntegerField(default=0, verbose_name='حداقل مبلغ سفارش (تومان)',
                                               validators=[MinValueValidator(0)])
    max_usage_total = models.PositiveIntegerField(default=0, verbose_name='حداکثر استفاده کل',
                                                   help_text='0 = بدون محدودیت')
    max_usage_per_user = models.PositiveIntegerField(default=1, verbose_name='حداکثر استفاده هر کاربر',
                                                      help_text='0 = بدون محدودیت')

    # محدودیت محصول/دسته‌بندی (اختیاری)
    limited_to_products = models.ManyToManyField('products.Product', blank=True,
                                                  verbose_name='محدود به محصولات',
                                                  help_text='خالی = همه محصولات')
    limited_to_categories = models.ManyToManyField('catalog.DesignType', blank=True,
                                                    verbose_name='محدود به دسته‌بندی (نوع طرح)',
                                                    help_text='خالی = همه دسته‌بندی‌ها')

    # تاریخ اعتبار
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')

    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    description = models.CharField(max_length=300, blank=True, verbose_name='توضیحات (داخلی)')

    # آمار
    usage_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کوپن تخفیف'
        verbose_name_plural = 'کوپن‌های تخفیف'
        ordering = ['-created_at']

    def __str__(self):
        if self.coupon_type == self.CouponType.PERCENT:
            return f'{self.code} ({self.amount}%)'
        return f'{self.code} ({self.amount:,} تومان)'

    @property
    def jalali_start(self):
        return jdatetime.datetime.fromgregorian(datetime=self.start_date).strftime('%Y/%m/%d')

    @property
    def jalali_end(self):
        return jdatetime.datetime.fromgregorian(datetime=self.end_date).strftime('%Y/%m/%d')

    @property
    def is_expired(self):
        return timezone.now() > self.end_date

    @property
    def is_not_started(self):
        return timezone.now() < self.start_date

    def is_valid(self):
        """بررسی اعتبار کلی کوپن"""
        if not self.is_active:
            return False, 'کوپن غیرفعال است.'
        if self.is_expired:
            return False, 'کوپن منقضی شده است.'
        if self.is_not_started:
            return False, 'کوپن هنوز فعال نشده است.'
        if self.max_usage_total > 0 and self.usage_count >= self.max_usage_total:
            return False, 'ظرفیت استفاده از این کوپن تکمیل شده.'
        return True, ''

    def is_valid_for_user(self, user):
        """بررسی اعتبار برای یک کاربر خاص"""
        valid, msg = self.is_valid()
        if not valid:
            return False, msg

        if self.max_usage_per_user > 0:
            user_count = self.usages.filter(user=user).count()
            if user_count >= self.max_usage_per_user:
                return False, 'شما قبلاً از این کوپن استفاده کرده‌اید.'

        return True, ''

    def is_valid_for_order(self, user, order_amount):
        """بررسی اعتبار برای سفارش"""
        valid, msg = self.is_valid_for_user(user)
        if not valid:
            return False, msg

        if order_amount < self.min_order_amount:
            return False, f'حداقل مبلغ سفارش برای این کوپن {self.min_order_amount:,} تومان است.'

        return True, ''

    def calculate_discount(self, order_amount):
        """محاسبه مبلغ تخفیف"""
        if self.coupon_type == self.CouponType.PERCENT:
            discount = int(order_amount * self.amount / 100)
            if self.max_discount and discount > self.max_discount:
                discount = self.max_discount
        else:
            discount = self.amount

        # تخفیف نباید بیشتر از مبلغ سفارش باشه
        if discount > order_amount:
            discount = order_amount

        return discount

    @staticmethod
    def generate_code(length=8):
        """تولید کد تصادفی"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=length))
            if not Coupon.objects.filter(code=code).exists():
                return code


class CouponUsage(models.Model):
    """لاگ استفاده از کوپن"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages', verbose_name='کوپن')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages',
                             verbose_name='کاربر')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='coupon_usages', verbose_name='سفارش')
    discount_amount = models.BigIntegerField(verbose_name='مبلغ تخفیف اعمال‌شده')
    used_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ استفاده')

    class Meta:
        verbose_name = 'استفاده از کوپن'
        verbose_name_plural = 'لاگ استفاده کوپن‌ها'
        ordering = ['-used_at']

    def __str__(self):
        return f'{self.coupon.code} → {self.user} ({self.discount_amount:,})'

    @property
    def jalali_used_at(self):
        return jdatetime.datetime.fromgregorian(datetime=self.used_at).strftime('%Y/%m/%d %H:%M')
