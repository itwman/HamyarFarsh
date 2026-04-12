"""
فاز 21: چت آنلاین و پشتیبانی
- ChatSession + ChatMessage: چت ساده (بدون نیاز به لاگین)
- Ticket + TicketReply: سیستم تیکت پشتیبانی (نیاز به لاگین)
"""
import uuid
import jdatetime
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """سشن چت آنلاین"""
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        ANSWERED = 'answered', 'پاسخ داده‌شده'
        CLOSED = 'closed', 'بسته'

    session_key = models.CharField(max_length=64, unique=True, default=uuid.uuid4, verbose_name='کلید سشن')
    visitor_name = models.CharField(max_length=100, verbose_name='نام بازدیدکننده')
    visitor_phone = models.CharField(max_length=15, blank=True, verbose_name='موبایل')
    visitor_email = models.CharField(max_length=200, blank=True, verbose_name='ایمیل')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='chat_sessions', verbose_name='کاربر')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN, verbose_name='وضعیت')
    page_url = models.CharField(max_length=500, blank=True, verbose_name='صفحه شروع چت')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='آدرس IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='شروع چت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین فعالیت')

    class Meta:
        verbose_name = 'سشن چت'
        verbose_name_plural = 'سشن‌های چت'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.visitor_name} ({self.get_status_display()})'

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')

    @property
    def unread_count(self):
        return self.messages.filter(is_admin=False, is_read=False).count()

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    """پیام چت"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='سشن')
    message = models.TextField(verbose_name='متن پیام')
    is_admin = models.BooleanField(default=False, verbose_name='پیام مدیر')
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='پاسخ‌دهنده')
    is_read = models.BooleanField(default=False, verbose_name='خوانده‌شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'پیام چت'
        verbose_name_plural = 'پیام‌های چت'
        ordering = ['created_at']

    def __str__(self):
        sender = 'مدیر' if self.is_admin else self.session.visitor_name
        return f'{sender}: {self.message[:40]}'

    @property
    def jalali_time(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%H:%M')


class Ticket(models.Model):
    """تیکت پشتیبانی"""
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        IN_PROGRESS = 'in_progress', 'در حال بررسی'
        ANSWERED = 'answered', 'پاسخ داده‌شده'
        CLOSED = 'closed', 'بسته'

    class Priority(models.TextChoices):
        LOW = 'low', 'کم'
        MEDIUM = 'medium', 'متوسط'
        HIGH = 'high', 'زیاد'
        URGENT = 'urgent', 'فوری'

    class Department(models.TextChoices):
        SALES = 'sales', 'فروش'
        SUPPORT = 'support', 'پشتیبانی'
        SHIPPING = 'shipping', 'ارسال'
        FINANCIAL = 'financial', 'مالی'
        OTHER = 'other', 'سایر'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='tickets', verbose_name='کاربر')
    subject = models.CharField(max_length=300, verbose_name='موضوع')
    department = models.CharField(max_length=15, choices=Department.choices,
                                  default=Department.SUPPORT, verbose_name='بخش')
    priority = models.CharField(max_length=10, choices=Priority.choices,
                                default=Priority.MEDIUM, verbose_name='اولویت')
    status = models.CharField(max_length=15, choices=Status.choices,
                              default=Status.OPEN, verbose_name='وضعیت')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='tickets', verbose_name='سفارش مرتبط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-updated_at']

    def __str__(self):
        return f'#{self.pk} {self.subject}'

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')

    @property
    def priority_color(self):
        return {'low': 'secondary', 'medium': 'info', 'high': 'warning', 'urgent': 'danger'}.get(self.priority, 'info')

    @property
    def status_color(self):
        return {'open': 'primary', 'in_progress': 'warning', 'answered': 'success', 'closed': 'secondary'}.get(self.status, 'info')


class TicketReply(models.Model):
    """پاسخ تیکت"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies', verbose_name='تیکت')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='فرستنده')
    message = models.TextField(verbose_name='متن پاسخ')
    attachment = models.FileField(upload_to='tickets/attachments/', blank=True, null=True, verbose_name='پیوست')
    is_admin = models.BooleanField(default=False, verbose_name='پاسخ مدیر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'پاسخ تیکت'
        verbose_name_plural = 'پاسخ‌های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f'پاسخ به #{self.ticket.pk} توسط {self.user}'

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')
