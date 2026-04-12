"""
مدل‌های سفارشات و سبد خرید
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import jdatetime

User = get_user_model()


class Order(models.Model):
    """مدل سفارش"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('reviewing', 'در حال بررسی'),
        ('confirmed', 'تأیید شده'),
        ('preparing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('online_full', 'نقدی آنلاین کامل'),
        ('deposit_on_delivery', 'بیعانه + پرداخت موقع تحویل'),
        ('installment_check', 'اقساطی چکی'),
        ('installment_beta', 'اقساطی بتا'),
    ]
    
    # اطلاعات پایه
    customer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='orders',
        verbose_name='مشتری'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    payment_method = models.CharField(
        max_length=30, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='روش پرداخت'
    )
    
    # مبالغ (به تومان - BigInteger)
    total_amount = models.BigIntegerField(
        verbose_name='مبلغ کل',
        validators=[MinValueValidator(0)]
    )
    deposit_amount = models.BigIntegerField(
        default=0,
        verbose_name='مبلغ بیعانه',
        validators=[MinValueValidator(0)]
    )
    paid_amount = models.BigIntegerField(
        default=0,
        verbose_name='مبلغ پرداخت شده',
        validators=[MinValueValidator(0)]
    )
    shipping_cost = models.BigIntegerField(
        default=0,
        verbose_name='هزینه ارسال',
        validators=[MinValueValidator(0)]
    )
    
    # آدرس ارسال
    shipping_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='آدرس ارسال',
        null=True,
        blank=True
    )
    
    # اطلاعات تکمیلی
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت مشتری'
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name='یادداشت مدیریت'
    )
    
    # قیمت روز (برای بیعانه‌ای‌ها)
    is_price_today = models.BooleanField(
        default=False,
        verbose_name='قیمت روز تحویل'
    )
    final_price_at_delivery = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت نهایی موقع تحویل',
        validators=[MinValueValidator(0)]
    )
    
    # ارسال رایگان
    free_shipping = models.BooleanField(
        default=False,
        verbose_name='ارسال رایگان'
    )

    # کوپن تخفیف (فاز 17)
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='کوپن تخفیف'
    )
    discount_amount = models.BigIntegerField(
        default=0,
        verbose_name='مبلغ تخفیف کوپن',
        validators=[MinValueValidator(0)]
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ تأیید'
    )
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ ارسال'
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ تحویل'
    )
    
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"سفارش #{self.id} - {self.customer.get_full_name()}"
    
    def get_jalali_created_at(self):
        """تاریخ ثبت شمسی"""
        if self.created_at:
            jdate = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            return jdate.strftime('%Y/%m/%d %H:%M')
        return ''
    
    def get_status_display_persian(self):
        """نمایش وضعیت به فارسی"""
        return dict(self.STATUS_CHOICES).get(self.status, '')
    
    def get_payment_method_display_persian(self):
        """نمایش روش پرداخت به فارسی"""
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, '')
    
    def get_remaining_amount(self):
        """محاسبه مانده پرداخت"""
        return self.total_amount - self.paid_amount
    
    def is_paid_full(self):
        """آیا کامل پرداخت شده؟"""
        return self.paid_amount >= self.total_amount
    
    def can_cancel(self):
        """آیا قابل لغو است؟"""
        return self.status in ['pending', 'reviewing']
    
    def calculate_cancellation_penalty(self):
        """محاسبه جریمه انصراف (50% بیعانه + ایاب‌ذهاب)"""
        if self.deposit_amount > 0:
            penalty = self.deposit_amount * 0.5
            # اضافه کردن هزینه ایاب‌ذهاب (فرضی: دو برابر هزینه ارسال)
            penalty += self.shipping_cost * 2
            return int(penalty)
        return 0


class OrderItem(models.Model):
    """آیتم سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        verbose_name='محصول'
    )
    size = models.ForeignKey(
        'catalog.CarpetSize',
        on_delete=models.PROTECT,
        verbose_name='سایز',
        null=True,
        blank=True
    )
    
    # سایز سفارشی
    is_custom_size = models.BooleanField(
        default=False,
        verbose_name='سایز سفارشی'
    )
    custom_length = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='طول سفارشی (متر)',
        validators=[MinValueValidator(0)]
    )
    custom_width = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='عرض سفارشی (متر)',
        validators=[MinValueValidator(0)]
    )
    custom_price_per_sqm = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت هر مترمربع (سفارشی)',
        validators=[MinValueValidator(0)]
    )
    
    # تعداد و قیمت
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد',
        validators=[MinValueValidator(1)]
    )
    unit_price = models.BigIntegerField(
        verbose_name='قیمت واحد',
        validators=[MinValueValidator(0)]
    )
    
    # زوج/فرد
    is_pair_order = models.BooleanField(
        default=False,
        verbose_name='سفارش زوجی'
    )
    
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
        ordering = ['id']
    
    def __str__(self):
        if self.is_custom_size:
            return f"{self.product.name} - سایز سفارشی ({self.custom_length}×{self.custom_width})"
        return f"{self.product.name} - {self.size.name if self.size else 'بدون سایز'}"
    
    def get_total_price(self):
        """محاسبه قیمت کل این آیتم"""
        return self.unit_price * self.quantity
    
    def get_custom_area(self):
        """محاسبه مساحت سایز سفارشی"""
        if self.is_custom_size and self.custom_length and self.custom_width:
            return float(self.custom_length) * float(self.custom_width)
        return 0


class OrderStatusLog(models.Model):
    """لاگ تغییر وضعیت سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='سفارش'
    )
    old_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت قبلی'
    )
    new_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت جدید'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='تغییر توسط'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ'
    )
    
    class Meta:
        verbose_name = 'لاگ وضعیت'
        verbose_name_plural = 'لاگ‌های وضعیت'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"سفارش #{self.order.id}: {self.old_status} → {self.new_status}"
    
    def get_jalali_created_at(self):
        """تاریخ شمسی"""
        if self.created_at:
            jdate = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            return jdate.strftime('%Y/%m/%d %H:%M')
        return ''
