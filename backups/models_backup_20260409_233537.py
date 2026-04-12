import math
import jdatetime
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from catalog.models import (
    Album, BackgroundColor, DesignType, WeaveType,
    Feature, ColorTone, CarpetSize
)
from settings_app.models import SiteSettings


class Product(models.Model):
    """محصول فرش - هسته اصلی سیستم"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'موجود'
        UNAVAILABLE = 'unavailable', 'ناموجود'
        EXHIBITION = 'exhibition', 'نمایشگاهی'
        COMING_SOON = 'coming_soon', 'به‌زودی'

    # اطلاعات اصلی
    name = models.CharField(max_length=300, verbose_name='نام نقشه')
    slug = models.SlugField(
        max_length=300, unique=True, allow_unicode=True,
        verbose_name='اسلاگ', blank=True
    )
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='products',
        verbose_name='آلبوم'
    )

    # دسته‌بندی‌ها
    background_color = models.ForeignKey(
        BackgroundColor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='رنگ زمینه'
    )
    design_type = models.ForeignKey(
        DesignType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='نوع طرح'
    )
    weave_type = models.ForeignKey(
        WeaveType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='نوع بافت'
    )
    feature = models.ForeignKey(
        Feature, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='ویژگی'
    )
    color_tone = models.ForeignKey(
        ColorTone, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='تناژ رنگ'
    )

    # قیمت خرید (override از آلبوم)
    purchase_price_12m = models.PositiveBigIntegerField(
        null=True, blank=True,
        verbose_name='قیمت خرید ۱۲ متری (تومان)',
        help_text='خالی باشد = از قیمت آلبوم استفاده می‌شود'
    )

    # وضعیت
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE,
        verbose_name='وضعیت'
    )
    is_featured = models.BooleanField(default=False, verbose_name='محصول ویژه')

    # SEO و محتوا
    seo_title = models.CharField(
        max_length=200, blank=True, verbose_name='عنوان SEO',
        help_text='خالی = تولید خودکار'
    )
    seo_description = models.TextField(
        blank=True, verbose_name='توضیحات SEO',
        help_text='خالی = تولید خودکار'
    )
    description = models.TextField(
        blank=True, verbose_name='شرح محصول (دستی)',
        help_text='خالی = شرح خودکار استفاده می‌شود'
    )

    # آمار
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    avg_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
        verbose_name='میانگین امتیاز'
    )
    rating_count = models.PositiveIntegerField(default=0, verbose_name='تعداد امتیاز')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['album']),
            models.Index(fields=['background_color']),
            models.Index(fields=['design_type']),
            models.Index(fields=['avg_rating']),
        ]

    def __str__(self):
        return f'{self.name} - {self.album}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f'{self.name}'
            if self.background_color:
                base += f'-{self.background_color.name}'
            base += f'-{self.album.comb}-شانه'
            self.slug = slugify(base, allow_unicode=True)
            # Ensure unique
            counter = 1
            orig_slug = self.slug
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{orig_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    # ===================== Properties =====================

    @property
    def manufacturer(self):
        return self.album.manufacturer

    @property
    def comb(self):
        return self.album.comb

    @property
    def density(self):
        return self.album.density

    @property
    def yarn_type(self):
        return self.album.get_yarn_type_display()

    @property
    def weight_class(self):
        return self.album.get_weight_class_display()

    @property
    def effective_purchase_price(self):
        """قیمت خرید مؤثر 12 متری"""
        return self.purchase_price_12m or self.album.base_price_12m or 0

    @property
    def jalali_created(self):
        if self.created_at:
            return jdatetime.datetime.fromgregorian(
                datetime=self.created_at
            ).strftime('%Y/%m/%d')
        return ''

    @property
    def primary_image(self):
        """تصویر شاخص"""
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def status_badge(self):
        badges = {
            'available': ('موجود', 'success'),
            'unavailable': ('ناموجود', 'secondary'),
            'exhibition': ('نمایشگاهی', 'info'),
            'coming_soon': ('به‌زودی', 'warning'),
        }
        return badges.get(self.status, ('نامشخص', 'dark'))

    # ===================== Pricing =====================

    def get_sell_price_12m(self):
        """قیمت فروش 12 متری"""
        settings = SiteSettings.get_solo()  # اصلاح شد: get_settings() -> get_solo()
        purchase = self.effective_purchase_price
        if not purchase:
            return 0

        profit_rate = Decimal(str(settings.profit_percent)) / Decimal('100')
        price_with_profit = Decimal(str(purchase)) * (1 + profit_rate)
        price_with_shipping = price_with_profit + Decimal(str(settings.shipping_cost))

        # گرد کردن به بالا
        step = Decimal(str(settings.rounding_step))
        if step > 0:
            price_rounded = math.ceil(float(price_with_shipping) / float(step)) * int(step)
        else:
            price_rounded = int(price_with_shipping)

        return price_rounded

    def get_price_per_sqm(self):
        """قیمت هر متر مربع بر اساس 12 متری"""
        price_12m = self.get_sell_price_12m()
        if price_12m:
            return price_12m / 12
        return 0

    def get_price_for_size(self, carpet_size):
        """
        محاسبه قیمت برای یک سایز خاص
        
        Args:
            carpet_size: شیء CarpetSize
        
        Returns:
            int: قیمت تومان
        """
        if not carpet_size:
            return 0
        
        # سایز 9 متری با پرتی
        if carpet_size.is_nine_meter:
            price_12m = self.get_sell_price_12m()
            base_price = Decimal(str(price_12m / 12)) * Decimal('9')  # قیمت 9 متری ساده
            
            waste_type = self.album.nine_m_waste_type
            waste_value = self.album.nine_m_waste_value or 0
            
            if waste_type == 'fixed':
                # پرتی ثابت
                final_price = base_price + Decimal(str(waste_value))
            else:  # percentage
                # پرتی درصدی
                waste_rate = Decimal(str(waste_value)) / Decimal('100')
                final_price = Decimal(str(base_price)) * (Decimal('1') + waste_rate)
            
            return int(final_price)
        
        # سایر سایزها
        price_per_sqm = self.get_price_per_sqm()
        total_price = Decimal(str(price_per_sqm)) * carpet_size.area
        
        return int(total_price)

    def get_size_price(self, carpet_size):
        """Alias برای سازگاری با کدهای قدیمی"""
        return self.get_price_for_size(carpet_size)

    def get_all_size_prices(self):
        """
        دریافت قیمت تمام سایزها
        
        Returns:
            list: لیست dict شامل سایز و قیمت
        """
        sizes = CarpetSize.objects.all().order_by('area')
        result = []
        
        for size in sizes:
            price = self.get_price_for_size(size)
            if price > 0:
                result.append({
                    'size': size,
                    'price': price,
                    'is_available': self.status == self.Status.AVAILABLE,
                    'order_rule': self.get_order_rule_for_size(size),
                })
        
        return result

    def get_order_rule_for_size(self, carpet_size):
        """
        دریافت قانون سفارش برای یک سایز
        
        Returns:
            str: 'free' یا 'even'
        """
        # بررسی قانون سفارشی محصول
        custom_rule = self.size_rules.filter(carpet_size=carpet_size).first()
        if custom_rule:
            return custom_rule.order_rule
        
        # قانون پیش‌فرض سایز
        return carpet_size.default_order_rule

    # ===================== SEO =====================

    def get_effective_seo_title(self):
        """عنوان SEO (دستی یا خودکار)"""
        if self.seo_title:
            return self.seo_title
        
        # تولید خودکار
        parts = [f'فرش {self.album.comb} شانه']
        if self.design_type:
            parts.append(self.design_type.name)
        parts.append(f'نقشه {self.name}')
        if self.background_color:
            parts.append(f'رنگ {self.background_color.name}')
        parts.append('| همیار فرش')
        
        return ' '.join(parts)

    def get_effective_seo_description(self):
        """توضیحات SEO (دستی یا خودکار)"""
        if self.seo_description:
            return self.seo_description
        
        # تولید خودکار
        parts = [f'خرید فرش {self.album.comb} شانه']
        if self.weave_type:
            parts.append(self.weave_type.name)
        if self.design_type:
            parts.append(f'طرح {self.design_type.name}')
        parts.append(f'نقشه {self.name}')
        if self.background_color:
            parts.append(f'با زمینه {self.background_color.name}')
        parts.append(f'جنس نخ {self.yarn_type}')
        if self.density:
            parts.append(f'تراکم {self.density}')
        
        price_12m = self.get_sell_price_12m()
        if price_12m:
            parts.append(f'قیمت از {price_12m:,} تومان')
        
        parts.append('ارسال رایگان خرید نقدی بالای 25 میلیون. خرید اقساطی تا 18 ماه.')
        
        return '، '.join(parts) + '.'

    def get_effective_description(self):
        """شرح محصول (دستی یا خودکار)"""
        if self.description:
            return self.description
        
        # تولید خودکار از قالب
        settings = SiteSettings.get_solo()
        template = settings.product_desc_template
        
        if template:
            return template.format(
                name=self.name,
                color=self.background_color.name if self.background_color else '',
                comb=self.album.comb,
                density=self.density or '',
                yarn=self.yarn_type,
                design=self.design_type.name if self.design_type else '',
                weave=self.weave_type.name if self.weave_type else '',
                price_12m=f'{self.get_sell_price_12m():,}'
            )
        
        # فرمت پیش‌فرض
        desc = f'''معرفی فرش {self.name}

فرش ماشینی {self.album.comb} شانه'''
        
        if self.design_type:
            desc += f' با طرح {self.design_type.name}'
        
        desc += f' و نقشه {self.name}'
        
        if self.background_color:
            desc += f' در رنگ زمینه {self.background_color.name}'
        
        desc += f'، تولید شرکت {self.manufacturer.name} از آلبوم {self.album.name}.'
        
        desc += f'''

مشخصات فنی:
• شانه: {self.album.comb}
• تراکم: {self.density or 'نامشخص'}
• جنس نخ: {self.yarn_type}
• وزن: {self.weight_class}'''
        
        if self.weave_type:
            desc += f'\n• نوع بافت: {self.weave_type.name}'
        
        if self.feature:
            desc += f'\n• ویژگی: {self.feature.name}'
        
        return desc


class ProductImage(models.Model):
    """تصاویر محصول"""
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images',
        verbose_name='محصول'
    )
    original = models.ImageField(
        upload_to='products/originals/', verbose_name='تصویر اصلی'
    )
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/', blank=True, null=True,
        verbose_name='تامبنیل'
    )
    featured_image = models.ImageField(
        upload_to='products/featured/', blank=True, null=True,
        verbose_name='تصویر شاخص 1000×1000'
    )
    
    is_primary = models.BooleanField(default=False, verbose_name='تصویر شاخص')
    alt_text = models.CharField(
        max_length=200, blank=True, verbose_name='متن جایگزین (alt)'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    
    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f'تصویر {self.product.name}'
    
    def get_effective_alt(self):
        """متن alt مؤثر (دستی یا خودکار)"""
        if self.alt_text:
            return self.alt_text
        
        # تولید خودکار
        parts = [f'فرش {self.product.name}']
        if self.product.background_color:
            parts.append(self.product.background_color.name)
        parts.append(f'{self.product.album.comb} شانه')
        
        return ' '.join(parts)
    
    def save(self, *args, **kwargs):
        # اگر این تصویر شاخص شد، بقیه رو غیرشاخص کن
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    """ویدیوهای محصول"""
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='videos',
        verbose_name='محصول'
    )
    video_file = models.FileField(
        upload_to='products/videos/', verbose_name='فایل ویدیو'
    )
    title = models.CharField(max_length=200, blank=True, verbose_name='عنوان')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    
    class Meta:
        verbose_name = 'ویدیوی محصول'
        verbose_name_plural = 'ویدیوهای محصولات'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f'ویدیو {self.product.name}'


class ProductSizeRule(models.Model):
    """قوانین سفارش سفارشی برای هر محصول و سایز"""
    
    ORDER_RULE_CHOICES = [
        ('free', 'آزاد'),
        ('even', 'فقط زوج'),
    ]
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='size_rules',
        verbose_name='محصول'
    )
    carpet_size = models.ForeignKey(
        CarpetSize, on_delete=models.CASCADE, verbose_name='سایز'
    )
    order_rule = models.CharField(
        max_length=10, choices=ORDER_RULE_CHOICES,
        verbose_name='قانون سفارش'
    )
    
    class Meta:
        verbose_name = 'قانون سفارش سایز'
        verbose_name_plural = 'قوانین سفارش سایزها'
        unique_together = ['product', 'carpet_size']
    
    def __str__(self):
        return f'{self.product.name} - {self.carpet_size.name}: {self.get_order_rule_display()}'


class ProductRating(models.Model):
    """امتیازدهی و نظرات محصول"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('approved', 'تأیید شده'),
        ('rejected', 'رد شده'),
    ]
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='ratings',
        verbose_name='محصول'
    )
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    related_name='product_ratings', verbose_name='کاربر'
    )
    
    rating = models.PositiveSmallIntegerField(
        verbose_name='امتیاز (1-5)',
        choices=[(i, f'{i} ستاره') for i in range(1, 6)]
    )
    comment = models.TextField(blank=True, verbose_name='نظر')
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
        verbose_name='وضعیت'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'امتیاز محصول'
        verbose_name_plural = 'امتیازات محصولات'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f'{self.user} - {self.product.name}: {self.rating} ستاره'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # بروزرسانی میانگین امتیاز محصول
        if self.status == 'approved':
            self.product.update_rating_stats()
