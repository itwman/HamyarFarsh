from django.db import models
from solo.models import SingletonModel


class SMSSettings(SingletonModel):
    """تنظیمات پیامک - مدل Singleton"""
    
    class Provider(models.TextChoices):
        KAVENEGAR = 'kavenegar', 'کاوه‌نگار'
        MELIPAYAMAK = 'melipayamak', 'ملی‌پیامک'
        SMSIR = 'smsir', 'SMS.ir'
    
    # تنظیمات عمومی
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.KAVENEGAR,
        verbose_name='سرویس دهنده پیامک'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='فعال بودن پیامک'
    )
    
    # کاوه‌نگار
    kavenegar_api_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='API Key کاوه‌نگار'
    )
    kavenegar_sender = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شماره ارسال کاوه‌نگار'
    )
    
    # ملی‌پیامک
    melipayamak_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='نام کاربری ملی‌پیامک'
    )
    melipayamak_password = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='رمز عبور ملی‌پیامک'
    )
    melipayamak_sender = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شماره ارسال ملی‌پیامک'
    )
    
    # SMS.ir
    smsir_api_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='API Key اس‌ام‌اس.آی‌آر'
    )
    smsir_line_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شماره خط اس‌ام‌اس.آی‌آر'
    )
    
    # قالب پیام‌ها
    welcome_sms_template = models.TextField(
        default='به {site_name} خوش آمدید! نام کاربری شما: {phone}',
        verbose_name='قالب پیامک خوش‌آمدگویی'
    )
    order_confirm_template = models.TextField(
        default='سفارش {order_id} شما با موفقیت ثبت شد. مبلغ: {amount} تومان',
        verbose_name='قالب پیامک تأیید سفارش'
    )
    order_status_template = models.TextField(
        default='سفارش {order_id} شما به مرحله {status} رسید.',
        verbose_name='قالب پیامک تغییر وضعیت'
    )
    payment_success_template = models.TextField(
        default='پرداخت {amount} تومان برای سفارش {order_id} با موفقیت انجام شد.',
        verbose_name='قالب پیامک تأیید پرداخت'
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'تنظیمات پیامک'
        verbose_name_plural = 'تنظیمات پیامک'
    
    def __str__(self):
        return f'تنظیمات پیامک ({self.get_provider_display()})'
