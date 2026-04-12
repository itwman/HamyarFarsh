"""
مدل کاتالوگ - فاز 11
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class Catalog(models.Model):
    """کاتالوگ اختصاصی محصولات"""
    
    # اطلاعات پایه
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان کاتالوگ'
    )
    unique_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='کد یکتا'
    )
    
    # ایجادکننده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='catalogs',
        verbose_name='ایجادشده توسط'
    )
    
    # محصولات
    products = models.ManyToManyField(
        'products.Product',
        related_name='in_catalogs',
        verbose_name='محصولات'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ انقضا'
    )
    
    # آمار
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد بازدید'
    )
    
    # یادداشت
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت'
    )
    
    class Meta:
        verbose_name = 'کاتالوگ'
        verbose_name_plural = 'کاتالوگ‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.unique_code})"
    
    def save(self, *args, **kwargs):
        # تولید کد یکتا
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        
        # تاریخ انقضا پیش‌فرض 30 روز
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_unique_code():
        """تولید کد یکتای 8 کاراکتری"""
        return uuid.uuid4().hex[:8].upper()
    
    def get_absolute_url(self):
        """لینک کاتالوگ"""
        from django.urls import reverse
        return reverse('catalog_app:view', kwargs={'code': self.unique_code})
    
    def is_expired(self):
        """بررسی انقضا"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def increment_view(self):
        """افزایش تعداد بازدید"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
