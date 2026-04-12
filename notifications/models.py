"""
فاز 19: نوار اعلان + اطلاع‌رسانی درون‌سایتی + پیامک خودکار
- Announcement: نوار اعلان بالای سایت
- Notification: اطلاع‌رسانی درون‌سایتی (زنگ)
- SMSTemplate: قالب پیامک خودکار
- SMSLog: لاگ ارسال پیامک
"""
import jdatetime
from django.db import models
from django.conf import settings
from django.utils import timezone


class Announcement(models.Model):
    """نوار اعلان بالای سایت"""
    text = models.CharField(max_length=500, verbose_name='متن اعلان')
    link = models.CharField(max_length=500, blank=True, verbose_name='لینک (اختیاری)')
    link_text = models.CharField(max_length=100, blank=True, verbose_name='متن لینک',
                                 help_text='مثال: مشاهده جزئیات')
    bg_color = models.CharField(max_length=7, default='#C62828', verbose_name='رنگ پس‌زمینه')
    text_color = models.CharField(max_length=7, default='#FFFFFF', verbose_name='رنگ متن')
    icon = models.CharField(max_length=50, blank=True, verbose_name='آیکون',
                            help_text='مثال: bi-megaphone, bi-percent, bi-gift')
    dismissible = models.BooleanField(default=True, verbose_name='قابل بستن توسط کاربر')
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.IntegerField(default=0, verbose_name='ترتیب')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'نوار اعلان‌ها'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.text[:50]

    @property
    def is_visible(self):
        if not self.is_active:
            return False
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @staticmethod
    def get_active():
        now = timezone.now()
        return Announcement.objects.filter(
            is_active=True, start_date__lte=now, end_date__gte=now
        ).order_by('order')


class Notification(models.Model):
    """اطلاع‌رسانی درون‌سایتی"""
    class NotifType(models.TextChoices):
        ORDER = 'order', 'سفارش'
        PAYMENT = 'payment', 'پرداخت'
        SYSTEM = 'system', 'سیستمی'
        DISCOUNT = 'discount', 'تخفیف'
        INFO = 'info', 'اطلاع‌رسانی'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='notifications', verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    message = models.TextField(verbose_name='متن')
    link = models.CharField(max_length=500, blank=True, verbose_name='لینک')
    notif_type = models.CharField(max_length=15, choices=NotifType.choices,
                                  default=NotifType.INFO, verbose_name='نوع')
    is_read = models.BooleanField(default=False, verbose_name='خوانده‌شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'اطلاع‌رسانی'
        verbose_name_plural = 'اطلاع‌رسانی‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.title} → {self.user}'

    @property
    def jalali_date(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')

    @property
    def icon(self):
        icons = {
            'order': 'bi-cart-check',
            'payment': 'bi-credit-card',
            'system': 'bi-gear',
            'discount': 'bi-percent',
            'info': 'bi-info-circle',
        }
        return icons.get(self.notif_type, 'bi-bell')

    @property
    def color(self):
        colors = {
            'order': 'primary',
            'payment': 'success',
            'system': 'secondary',
            'discount': 'danger',
            'info': 'info',
        }
        return colors.get(self.notif_type, 'info')

    @staticmethod
    def create_for_user(user, title, message, notif_type='info', link=''):
        return Notification.objects.create(
            user=user, title=title, message=message,
            notif_type=notif_type, link=link
        )

    @staticmethod
    def unread_count(user):
        return Notification.objects.filter(user=user, is_read=False).count()


class SMSTemplate(models.Model):
    """قالب پیامک خودکار"""
    class Event(models.TextChoices):
        ORDER_CREATED = 'order_created', 'ثبت سفارش جدید (به مشتری)'
        ORDER_CREATED_ADMIN = 'order_created_admin', 'ثبت سفارش جدید (به مدیر)'
        ORDER_CONFIRMED = 'order_confirmed', 'تأیید سفارش'
        ORDER_SHIPPED = 'order_shipped', 'ارسال سفارش'
        ORDER_DELIVERED = 'order_delivered', 'تحویل سفارش'
        PAYMENT_SUCCESS = 'payment_success', 'پرداخت موفق'
        INSTALLMENT_DUE = 'installment_due', 'یادآوری قسط'

    event = models.CharField(max_length=30, choices=Event.choices, unique=True, verbose_name='رویداد')
    template = models.TextField(verbose_name='قالب پیامک',
                                help_text='متغیرها: {name}, {order_id}, {amount}, {site_name}, {status}')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'قالب پیامک'
        verbose_name_plural = 'قالب‌های پیامک'

    def __str__(self):
        return self.get_event_display()

    def render(self, **kwargs):
        text = self.template
        for key, val in kwargs.items():
            text = text.replace('{' + key + '}', str(val))
        return text


class SMSLog(models.Model):
    """لاگ ارسال پیامک"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'در صف'
        SENT = 'sent', 'ارسال‌شده'
        FAILED = 'failed', 'ناموفق'

    phone = models.CharField(max_length=15, verbose_name='شماره')
    message = models.TextField(verbose_name='متن پیامک')
    event = models.CharField(max_length=30, blank=True, verbose_name='رویداد')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING,
                              verbose_name='وضعیت')
    api_response = models.TextField(blank=True, verbose_name='پاسخ API')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'لاگ پیامک'
        verbose_name_plural = 'لاگ پیامک‌ها'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.phone} - {self.get_status_display()}'

    @property
    def jalali_date(self):
        return jdatetime.datetime.fromgregorian(datetime=self.sent_at).strftime('%Y/%m/%d %H:%M')
