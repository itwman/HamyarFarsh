from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """مدیر کاربر سفارشی - ورود با شماره موبایل"""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره موبایل الزامی است.')
        extra_fields.setdefault('username', phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('username', phone)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """مدل کاربر سفارشی همیار فرش"""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'مدیر'
        STAFF = 'staff', 'کارمند'
        CUSTOMER = 'customer', 'مشتری'

    phone = models.CharField(
        max_length=11, unique=True, verbose_name='شماره موبایل',
        help_text='شماره موبایل 11 رقمی (مثال: 09121234567)'
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER,
        verbose_name='نقش'
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True,
        verbose_name='تصویر پروفایل'
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name() or self.phone} ({self.get_role_display()})'

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_staff_user(self):
        return self.role in (self.Role.ADMIN, self.Role.STAFF) or self.is_superuser


class Address(models.Model):
    """آدرس ارسال مشتری"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses',
        verbose_name='کاربر'
    )
    province = models.CharField(max_length=50, verbose_name='استان')
    city = models.CharField(max_length=50, verbose_name='شهر')
    full_address = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name='کد پستی'
    )
    phone = models.CharField(
        max_length=11, blank=True, verbose_name='تلفن تماس'
    )
    is_default = models.BooleanField(default=False, verbose_name='آدرس پیش‌فرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.province}، {self.city} - {self.user}'

    def get_full_address(self):
        """بازگشت آدرس کامل به صورت فرمت شده"""
        parts = [self.province, self.city, self.full_address]
        if self.postal_code:
            parts.append(f'کد پستی: {self.postal_code}')
        return '، '.join(parts)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
