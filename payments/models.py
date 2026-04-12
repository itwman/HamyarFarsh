from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
from django.utils import timezone

User = get_user_model()


class PaymentGateway(models.Model):
    """تنظیمات درگاه‌های پرداخت"""
    
    GATEWAY_CHOICES = [
        ('zarinpal', 'زرین‌پال'),
        ('saman', 'سامان'),
        ('mellat', 'ملت'),
        ('parsian', 'پارسیان'),
    ]
    
    name = models.CharField('نام درگاه', max_length=50, choices=GATEWAY_CHOICES, unique=True)
    merchant_id = models.CharField('شناسه پذیرنده', max_length=100)
    terminal_id = models.CharField('شناسه ترمینال', max_length=100, blank=True)
    api_key = models.CharField('کلید API', max_length=200, blank=True)
    is_active = models.BooleanField('فعال', default=True)
    is_sandbox = models.BooleanField('حالت تست', default=False)
    
    class Meta:
        db_table = 'payment_gateways'
        verbose_name = 'درگاه پرداخت'
        verbose_name_plural = 'درگاه‌های پرداخت'
    
    def __str__(self):
        return self.get_name_display()


class Transaction(models.Model):
    """تراکنش‌های پرداخت"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('processing', 'در حال پردازش'),
        ('completed', 'موفق'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'برگشت داده شده'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions', verbose_name='سفارش')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, verbose_name='درگاه پرداخت')
    
    # مبالغ
    amount = models.DecimalField('مبلغ (تومان)', max_digits=12, decimal_places=0)
    
    # شناسه‌ها
    tracking_code = models.CharField('کد پیگیری سیستم', max_length=50, unique=True, db_index=True)
    authority = models.CharField('شناسه تراکنش درگاه', max_length=100, blank=True, db_index=True)
    reference_number = models.CharField('شماره مرجع', max_length=100, blank=True, db_index=True)
    
    # وضعیت
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # IP و User Agent
    ip_address = models.GenericIPAddressField('آی‌پی', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    # تاریخ‌ها
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True, db_index=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)
    
    # پاسخ درگاه
    gateway_response = models.JSONField('پاسخ درگاه', default=dict, blank=True)
    error_message = models.TextField('پیام خطا', blank=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
            models.Index(fields=['order', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.tracking_code} - {self.get_status_display()}'
    
    def mark_as_completed(self, reference_number, gateway_response=None):
        """علامت‌گذاری به عنوان موفق"""
        self.status = 'completed'
        self.reference_number = reference_number
        self.paid_at = timezone.now()
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()
    
    def mark_as_failed(self, error_message):
        """علامت‌گذاری به عنوان ناموفق"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class InstallmentPlan(models.Model):
    """طرح‌های اقساط"""
    
    PLAN_TYPE_CHOICES = [
        ('check', 'چک صیادی'),
        ('beta', 'طرح بتا (بانک رفاه)'),
    ]
    
    PERIOD_CHOICES = [
        ('monthly', 'ماهانه'),
        ('bimonthly', 'دوماهانه'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='installment_plan', verbose_name='سفارش')
    plan_type = models.CharField('نوع طرح', max_length=20, choices=PLAN_TYPE_CHOICES)
    
    # مبالغ
    total_amount = models.DecimalField('مبلغ کل فاکتور', max_digits=12, decimal_places=0)
    down_payment = models.DecimalField('پیش‌پرداخت', max_digits=12, decimal_places=0, default=0)
    financed_amount = models.DecimalField('مبلغ قابل اقساط', max_digits=12, decimal_places=0)
    interest_rate = models.DecimalField('نرخ سود ماهانه (%)', max_digits=5, decimal_places=2)
    total_interest = models.DecimalField('مجموع سود', max_digits=12, decimal_places=0)
    total_with_interest = models.DecimalField('مبلغ کل با سود', max_digits=12, decimal_places=0)
    
    # اقساط
    num_installments = models.PositiveIntegerField('تعداد اقساط')
    period = models.CharField('دوره پرداخت', max_length=20, choices=PERIOD_CHOICES, default='monthly')
    installment_amount = models.DecimalField('مبلغ هر قسط', max_digits=12, decimal_places=0)
    
    # تاریخ‌ها
    first_due_date = models.DateField('تاریخ سررسید اول', null=True, blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    
    # تأیید
    is_confirmed = models.BooleanField('تأیید شده', default=False)
    confirmed_at = models.DateTimeField('تاریخ تأیید', null=True, blank=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='confirmed_installments', verbose_name='تأیید کننده')
    
    class Meta:
        db_table = 'installment_plans'
        verbose_name = 'طرح اقساط'
        verbose_name_plural = 'طرح‌های اقساط'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'اقساط {self.get_plan_type_display()} - سفارش {self.order.id}'
    
    def calculate_installment_amount(self):
        """محاسبه مبلغ هر قسط"""
        if self.num_installments > 0:
            return int(self.total_with_interest / self.num_installments)
        return 0
    
    def save(self, *args, **kwargs):
        # محاسبه خودکار مقادیر
        self.financed_amount = self.total_amount - self.down_payment
        
        # محاسبه سود
        months = self.num_installments if self.period == 'monthly' else self.num_installments * 2
        self.total_interest = self.financed_amount * (self.interest_rate / 100) * months
        self.total_with_interest = self.financed_amount + self.total_interest
        
        # محاسبه مبلغ هر قسط
        self.installment_amount = self.calculate_installment_amount()
        
        super().save(*args, **kwargs)


class Installment(models.Model):
    """اقساط تفکیک شده"""
    
    STATUS_CHOICES = [
        ('pending', 'پرداخت نشده'),
        ('paid', 'پرداخت شده'),
        ('overdue', 'سررسید گذشته'),
        ('cancelled', 'لغو شده'),
    ]
    
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='installments', verbose_name='طرح اقساط')
    
    installment_number = models.PositiveIntegerField('شماره قسط')
    amount = models.DecimalField('مبلغ قسط', max_digits=12, decimal_places=0)
    due_date = models.DateField('تاریخ سررسید')
    
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)
    
    # در صورت پرداخت آنلاین
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='installment_payments', verbose_name='تراکنش')
    
    # شماره چک (برای طرح چکی)
    check_number = models.CharField('شماره چک', max_length=50, blank=True)
    bank_name = models.CharField('نام بانک', max_length=100, blank=True)
    
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    
    class Meta:
        db_table = 'installments'
        verbose_name = 'قسط'
        verbose_name_plural = 'اقساط'
        ordering = ['plan', 'installment_number']
        unique_together = ['plan', 'installment_number']
    
    def __str__(self):
        return f'قسط {self.installment_number} - {self.plan}'
    
    def is_overdue(self):
        """آیا سررسید گذشته است؟"""
        from datetime import date
        return self.status == 'pending' and self.due_date < date.today()
    
    def mark_as_paid(self, transaction=None):
        """علامت‌گذاری به عنوان پرداخت شده"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        if transaction:
            self.transaction = transaction
        self.save()
