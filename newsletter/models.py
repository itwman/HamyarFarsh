"""
فاز 20: خبرنامه پیامکی و بازاریابی (SMS Marketing)
- NewsletterSubscriber: جمع‌آوری شماره مشتریان
- SMSCampaign: ارسال انبوه پیامک (دستی/خودکار)
- CampaignLog: لاگ ارسال هر پیامک کمپین
"""
import jdatetime
import re
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


PHONE_REGEX = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد.'
)


class NewsletterSubscriber(models.Model):
    """مشترک خبرنامه پیامکی"""

    class Source(models.TextChoices):
        FOOTER = 'footer', 'فرم فوتر'
        POPUP = 'popup', 'پاپ‌آپ'
        MANUAL = 'manual', 'افزودن دستی'
        IMPORT = 'import', 'واردکردن فایل'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'فعال'
        UNSUBSCRIBED = 'unsubscribed', 'لغو عضویت'

    phone = models.CharField(max_length=11, unique=True, verbose_name='شماره موبایل',
                             validators=[PHONE_REGEX])
    name = models.CharField(max_length=100, blank=True, verbose_name='نام (اختیاری)')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE,
                              verbose_name='وضعیت')
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.FOOTER,
                              verbose_name='منبع عضویت')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='newsletter_subs',
                             verbose_name='کاربر سایت')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ لغو')

    class Meta:
        verbose_name = 'مشترک خبرنامه'
        verbose_name_plural = 'مشترکین خبرنامه'
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.phone} ({self.name or "-"})'

    @property
    def jalali_subscribed(self):
        return jdatetime.datetime.fromgregorian(datetime=self.subscribed_at).strftime('%Y/%m/%d %H:%M')


class SMSCampaign(models.Model):
    """کمپین ارسال انبوه پیامک"""

    class CampaignStatus(models.TextChoices):
        DRAFT = 'draft', 'پیش‌نویس'
        SENDING = 'sending', 'در حال ارسال'
        COMPLETED = 'completed', 'تکمیل‌شده'
        CANCELLED = 'cancelled', 'لغو‌شده'

    class RecipientType(models.TextChoices):
        ALL_ACTIVE = 'all_active', 'همه مشترکین فعال'
        SELECTED = 'selected', 'انتخابی'
        SITE_USERS = 'site_users', 'مشتریان سایت'

    title = models.CharField(max_length=200, verbose_name='عنوان کمپین')
    message = models.TextField(verbose_name='متن پیامک',
                               help_text='متغیرها: {name} نام مشترک، {site_name} نام سایت')
    recipient_type = models.CharField(max_length=15, choices=RecipientType.choices,
                                      default=RecipientType.ALL_ACTIVE, verbose_name='گیرندگان')
    status = models.CharField(max_length=15, choices=CampaignStatus.choices,
                              default=CampaignStatus.DRAFT, verbose_name='وضعیت')

    # آمار
    total_recipients = models.PositiveIntegerField(default=0, verbose_name='تعداد گیرندگان')
    sent_count = models.PositiveIntegerField(default=0, verbose_name='ارسال‌شده')
    failed_count = models.PositiveIntegerField(default=0, verbose_name='ناموفق')

    # زمان
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان‌بندی ارسال',
                                        help_text='خالی = ارسال فوری')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ ارسال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, verbose_name='ایجادکننده')

    class Meta:
        verbose_name = 'کمپین پیامکی'
        verbose_name_plural = 'کمپین‌های پیامکی'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d')

    @property
    def jalali_sent(self):
        if self.sent_at:
            return jdatetime.datetime.fromgregorian(datetime=self.sent_at).strftime('%Y/%m/%d %H:%M')
        return '-'

    def render_message(self, subscriber=None):
        """رندر متن پیامک با متغیرها"""
        from settings_app.models import SiteSettings
        ss = SiteSettings.get_solo()
        text = self.message
        text = text.replace('{site_name}', ss.site_name)
        if subscriber:
            text = text.replace('{name}', subscriber.name or 'مشتری عزیز')
        else:
            text = text.replace('{name}', 'مشتری عزیز')
        return text

    def get_recipients(self):
        """دریافت لیست گیرندگان"""
        if self.recipient_type == self.RecipientType.ALL_ACTIVE:
            return NewsletterSubscriber.objects.filter(status='active')
        elif self.recipient_type == self.RecipientType.SITE_USERS:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            phones = User.objects.filter(is_active=True).exclude(
                phone=''
            ).values_list('phone', flat=True)
            return NewsletterSubscriber.objects.filter(phone__in=phones, status='active')
        return NewsletterSubscriber.objects.none()


class CampaignLog(models.Model):
    """لاگ ارسال هر پیامک کمپین"""
    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, related_name='logs',
                                 verbose_name='کمپین')
    phone = models.CharField(max_length=15, verbose_name='شماره')
    status = models.CharField(max_length=10, choices=[
        ('sent', 'ارسال‌شده'), ('failed', 'ناموفق')
    ], verbose_name='وضعیت')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'لاگ کمپین'
        verbose_name_plural = 'لاگ‌های کمپین'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.campaign.title} → {self.phone}'
