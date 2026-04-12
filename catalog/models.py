from django.db import models
from django.utils.text import slugify
import jdatetime
import math


class Manufacturer(models.Model):
    """شرکت تولیدی فرش"""
    name = models.CharField(max_length=200, verbose_name='نام شرکت')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    logo = models.ImageField(
        upload_to='logos/manufacturers/', blank=True, null=True,
        verbose_name='لوگو'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='موبایل')
    website = models.URLField(blank=True, verbose_name='وب‌سایت')
    address = models.TextField(blank=True, verbose_name='آدرس')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.IntegerField(default=0, verbose_name='ترتیب نمایش')
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان SEO')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'شرکت تولیدی'
        verbose_name_plural = 'شرکت‌های تولیدی'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def jalali_created(self):
        if self.created_at:
            return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d')
        return ''

    def get_album_count(self):
        """تعداد آلبوم‌ها - متد (نه property) برای سازگاری با annotate"""
        return self.albums.count()

    def get_active_album_count(self):
        """تعداد آلبوم‌های فعال"""
        return self.albums.filter(is_active=True).count()


class Album(models.Model):
    """آلبوم محصولات هر شرکت"""

    class YarnType(models.TextChoices):
        ACRYLIC = 'acrylic', 'آکرلیک'
        POLYESTER = 'polyester', 'پلی‌استر'
        BCF = 'bcf', 'BCF'
        HEAT_SET = 'heat_set', 'هیت‌ست'
        OTHER = 'other', 'سایر'

    class WeightClass(models.TextChoices):
        LIGHT = 'light', 'سبک'
        HEAVY = 'heavy', 'سنگین'
        MEDIUM = 'medium', 'متوسط'

    class WasteType(models.TextChoices):
        FIXED = 'fixed', 'عدد ثابت (تومان)'
        PERCENT = 'percent', 'درصدی'

    COMB_CHOICES = [
        (700, '۷۰۰ شانه'),
        (1000, '۱۰۰۰ شانه'),
        (1200, '۱۲۰۰ شانه'),
        (1500, '۱۵۰۰ شانه'),
    ]

    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, related_name='albums',
        verbose_name='شرکت تولیدی'
    )
    name = models.CharField(max_length=200, verbose_name='نام آلبوم')
    slug = models.SlugField(max_length=200, allow_unicode=True, verbose_name='اسلاگ')
    comb = models.PositiveIntegerField(
        choices=COMB_CHOICES, verbose_name='شانه'
    )
    density = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='تراکم'
    )
    yarn_type = models.CharField(
        max_length=20, choices=YarnType.choices, default=YarnType.ACRYLIC,
        verbose_name='جنس نخ'
    )
    weight_class = models.CharField(
        max_length=20, choices=WeightClass.choices, default=WeightClass.HEAVY,
        verbose_name='وزن'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')

    # پرتی 9 متری
    nine_m_waste_type = models.CharField(
        max_length=10, choices=WasteType.choices, default=WasteType.FIXED,
        verbose_name='نوع پرتی ۹ متری'
    )
    nine_m_waste_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name='مقدار پرتی',
        help_text='برای ثابت: مبلغ به تومان / برای درصدی: عدد درصد (مثلاً 10)'
    )

    # قیمت پایه
    base_price_12m = models.PositiveBigIntegerField(
        null=True, blank=True,
        verbose_name='قیمت خرید پایه ۱۲ متری (تومان)'
    )

    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.IntegerField(default=0, verbose_name='ترتیب نمایش')
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان SEO')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'آلبوم'
        verbose_name_plural = 'آلبوم‌ها'
        ordering = ['manufacturer', 'sort_order', 'name']
        unique_together = [('manufacturer', 'slug')]

    def __str__(self):
        return f'{self.name} ({self.manufacturer.name} - {self.get_comb_display()})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def jalali_created(self):
        if self.created_at:
            return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d')
        return ''

    @property
    def comb_display(self):
        return f'{self.comb} شانه'

    @property
    def waste_display(self):
        if self.nine_m_waste_type == self.WasteType.FIXED:
            return f'{self.nine_m_waste_value:,.0f} تومان'
        return f'{self.nine_m_waste_value}%'


# ============================================================
# فاز 3: دسته‌بندی‌ها و ویژگی‌های فرش
# ============================================================

class BackgroundColor(models.Model):
    """رنگ زمینه فرش"""
    name = models.CharField(max_length=100, unique=True, verbose_name='نام رنگ')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    color_code = models.CharField(
        max_length=7, blank=True, verbose_name='کد رنگ HEX',
        help_text='مثال: #1A237E'
    )
    sort_order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'رنگ زمینه'
        verbose_name_plural = 'رنگ‌های زمینه'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class DesignType(models.Model):
    """نوع طرح فرش"""
    name = models.CharField(max_length=100, unique=True, verbose_name='نام طرح')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    description = models.TextField(blank=True, verbose_name='توضیح SEO')
    sort_order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'نوع طرح'
        verbose_name_plural = 'انواع طرح'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class WeaveType(models.Model):
    """نوع بافت"""
    name = models.CharField(max_length=100, unique=True, verbose_name='نوع بافت')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'نوع بافت'
        verbose_name_plural = 'انواع بافت'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Feature(models.Model):
    """ویژگی فرش (گل‌برجسته، ساده، ...)"""
    name = models.CharField(max_length=100, unique=True, verbose_name='ویژگی')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class ColorTone(models.Model):
    """تناژ رنگ"""
    name = models.CharField(max_length=50, unique=True, verbose_name='تناژ رنگ')
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'تناژ رنگ'
        verbose_name_plural = 'تناژهای رنگ'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ============================================================
# فاز 3.2: سایزهای فرش
# ============================================================

class CarpetSize(models.Model):
    """سایزهای استاندارد فرش"""

    class OrderRule(models.TextChoices):
        ANY = 'any', 'آزاد (هر تعداد)'
        EVEN = 'even', 'فقط زوج (جفتی)'

    class SizeType(models.TextChoices):
        RECTANGULAR = 'rectangular', 'مستطیل / مربع'
        ROUND = 'round', 'گرد'
        RUNNER = 'runner', 'کناره'
        DOORMAT = 'doormat', 'پادری'
        CUSHION = 'cushion', 'رویه پشتی'

    name = models.CharField(max_length=100, verbose_name='نام سایز')
    size_type = models.CharField(
        max_length=20, choices=SizeType.choices, default=SizeType.RECTANGULAR,
        verbose_name='نوع سایز'
    )

    length = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='طول (متر)'
    )
    width = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='عرض (متر)'
    )
    diameter = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='قطر (متر) - فقط برای گرد'
    )

    area = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name='مساحت (متر مربع)',
        help_text='برای مستطیل: طول×عرض / برای گرد: π×(قطر/2)²'
    )

    is_nine_meter = models.BooleanField(
        default=False, verbose_name='سایز ۹ متری (۳.۵۰×۲.۵۰)',
        help_text='اگر بله، قیمت با فرمول پرتی محاسبه می‌شود'
    )

    default_order_rule = models.CharField(
        max_length=10, choices=OrderRule.choices, default=OrderRule.ANY,
        verbose_name='قانون سفارش پیش‌فرض'
    )

    sort_order = models.IntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'سایز فرش'
        verbose_name_plural = 'سایزهای فرش'
        ordering = ['sort_order', '-area']

    def __str__(self):
        if self.size_type == self.SizeType.ROUND:
            return f'{self.name} (قطر {self.diameter} متر - {self.area:.2f} م²)'
        return f'{self.name} ({self.length}×{self.width} - {self.area:.2f} م²)'

    def save(self, *args, **kwargs):
        if self.size_type == self.SizeType.ROUND and self.diameter:
            self.area = round(math.pi * (float(self.diameter) / 2) ** 2, 4)
        elif self.length and self.width:
            self.area = round(float(self.length) * float(self.width), 4)
        super().save(*args, **kwargs)

    @property
    def dimensions_display(self):
        if self.size_type == self.SizeType.ROUND:
            return f'قطر {self.diameter} متر'
        return f'{self.length}×{self.width} متر'

    @property
    def area_display(self):
        return f'{self.area:.2f} متر مربع'

    @property
    def order_rule_display(self):
        if self.default_order_rule == self.OrderRule.EVEN:
            return 'فقط زوج (جفتی)'
        return 'آزاد'
