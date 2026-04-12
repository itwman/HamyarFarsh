"""
فاز 15: مدیریت صفحه اصلی
- اسلایدر (HomeSlider)
- بنرهای تبلیغاتی (HomeBanner)
- بخش‌های سفارشی (HomeSection)
"""
from django.db import models
from django.utils import timezone


class HomeSlider(models.Model):
    """اسلایدر صفحه اصلی"""
    title = models.CharField(max_length=200, verbose_name='عنوان')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='زیرعنوان')
    button_text = models.CharField(max_length=100, blank=True, verbose_name='متن دکمه')
    button_link = models.CharField(max_length=500, blank=True, verbose_name='لینک دکمه')

    image_desktop = models.ImageField(upload_to='sliders/', verbose_name='تصویر دسکتاپ (1920×600)')
    image_mobile = models.ImageField(upload_to='sliders/', blank=True, null=True,
                                     verbose_name='تصویر موبایل (768×400)', help_text='خالی = همان دسکتاپ')

    # تنظیمات نمایش
    text_color = models.CharField(max_length=7, default='#FFFFFF', verbose_name='رنگ متن')
    overlay_opacity = models.IntegerField(default=30, verbose_name='تاریکی پس‌زمینه (%)',
                                          help_text='0=شفاف، 100=کاملاً تاریک')

    order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ شروع نمایش')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پایان نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'اسلاید'
        verbose_name_plural = 'اسلایدر صفحه اصلی'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_visible(self):
        """آیا الان قابل نمایش است؟"""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class HomeBanner(models.Model):
    """بنرهای تبلیغاتی"""
    class Position(models.TextChoices):
        TOP = 'top', 'بالای محصولات'
        MIDDLE = 'middle', 'وسط صفحه'
        BOTTOM = 'bottom', 'پایین صفحه'

    class Width(models.TextChoices):
        FULL = 'full', 'تمام‌عرض'
        HALF = 'half', 'نیمه'

    title = models.CharField(max_length=200, verbose_name='عنوان (داخلی)')
    image = models.ImageField(upload_to='banners/', verbose_name='تصویر بنر')
    link = models.CharField(max_length=500, blank=True, verbose_name='لینک')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='متن alt')

    position = models.CharField(max_length=10, choices=Position.choices, default=Position.TOP, verbose_name='موقعیت')
    width = models.CharField(max_length=10, choices=Width.choices, default=Width.FULL, verbose_name='عرض')

    order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='شروع نمایش')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='پایان نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بنر تبلیغاتی'
        verbose_name_plural = 'بنرهای تبلیغاتی'
        ordering = ['position', 'order']

    def __str__(self):
        return f'{self.title} ({self.get_position_display()})'

    @property
    def is_visible(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class HomeSection(models.Model):
    """بخش‌های سفارشی صفحه اصلی"""
    class SectionType(models.TextChoices):
        PRODUCT_AUTO = 'product_auto', 'محصولات خودکار'
        PRODUCT_MANUAL = 'product_manual', 'محصولات دستی'
        HTML_CUSTOM = 'html_custom', 'کد HTML سفارشی'
        BLOG_POSTS = 'blog_posts', 'آخرین مقالات'
        BRANDS = 'brands', 'لوگوی شرکت‌ها'

    class AutoFilter(models.TextChoices):
        NEWEST = 'newest', 'جدیدترین'
        FEATURED = 'featured', 'ویژه'
        POPULAR = 'popular', 'پربازدید'
        CHEAPEST = 'cheapest', 'ارزان‌ترین'

    title = models.CharField(max_length=200, verbose_name='عنوان بخش')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='زیرعنوان')
    icon = models.CharField(max_length=50, blank=True, verbose_name='آیکون Bootstrap',
                            help_text='مثال: bi-fire, bi-star-fill, bi-lightning')

    section_type = models.CharField(max_length=20, choices=SectionType.choices, verbose_name='نوع بخش')

    # فیلتر خودکار (برای product_auto)
    auto_filter = models.CharField(max_length=20, choices=AutoFilter.choices, default=AutoFilter.NEWEST,
                                   blank=True, verbose_name='فیلتر خودکار')
    auto_comb = models.IntegerField(null=True, blank=True, verbose_name='فیلتر شانه',
                                     help_text='خالی = همه شانه‌ها')

    # محصولات دستی (برای product_manual)
    manual_products = models.ManyToManyField('products.Product', blank=True, verbose_name='محصولات انتخابی')

    # HTML سفارشی
    html_content = models.TextField(blank=True, verbose_name='کد HTML')

    # تنظیمات
    item_count = models.IntegerField(default=8, verbose_name='تعداد آیتم')
    bg_color = models.CharField(max_length=7, blank=True, verbose_name='رنگ پس‌زمینه',
                                help_text='خالی = شفاف. مثال: #F5F5F5')
    show_more_link = models.CharField(max_length=500, blank=True, verbose_name='لینک «مشاهده بیشتر»')

    order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بخش صفحه اصلی'
        verbose_name_plural = 'بخش‌های صفحه اصلی'
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.get_section_type_display()})'

    def get_products(self):
        """دریافت محصولات بر اساس نوع بخش"""
        from products.models import Product

        if self.section_type == self.SectionType.PRODUCT_MANUAL:
            return self.manual_products.filter(
                status='available'
            ).select_related('album__manufacturer', 'background_color').prefetch_related(
                'design_type', 'images'
            )[:self.item_count]

        if self.section_type == self.SectionType.PRODUCT_AUTO:
            qs = Product.objects.filter(
                status__in=['available', 'coming_soon']
            ).select_related('album__manufacturer', 'background_color').prefetch_related(
                'design_type', 'images'
            )

            if self.auto_comb:
                qs = qs.filter(album__comb=self.auto_comb)

            if self.auto_filter == self.AutoFilter.FEATURED:
                qs = qs.filter(is_featured=True).order_by('-created_at')
            elif self.auto_filter == self.AutoFilter.POPULAR:
                qs = qs.order_by('-view_count')
            elif self.auto_filter == self.AutoFilter.CHEAPEST:
                qs = qs.order_by('purchase_price_12m')
            else:  # newest
                qs = qs.order_by('-created_at')

            return qs[:self.item_count]

        return []

    def get_blog_posts(self):
        """آخرین مقالات"""
        from pages.models import Page
        return Page.objects.filter(
            status='published', page_type='post'
        ).order_by('-publish_date', '-created_at')[:self.item_count]

    def get_brands(self):
        """لوگوی شرکت‌های فعال"""
        from catalog.models import Manufacturer
        return Manufacturer.objects.filter(is_active=True).order_by('name')
