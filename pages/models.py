"""
فاز 14: سیستم مدیریت محتوا (CMS)
- صفحات ایستا (درباره ما، نحوه خرید، ...)
- مقالات/بلاگ با دسته‌بندی
- ویرایشگر WYSIWYG (TinyMCE/Summernote)
- SEO کامل (Schema.org Article/WebPage)
"""
import jdatetime
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class PostCategory(models.Model):
    """دسته‌بندی مقالات"""
    name = models.CharField(max_length=200, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    image = models.ImageField(upload_to='pages/categories/', blank=True, null=True, verbose_name='تصویر')
    sort_order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # SEO
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان SEO')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO')

    class Meta:
        verbose_name = 'دسته‌بندی مقالات'
        verbose_name_plural = 'دسته‌بندی‌های مقالات'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def published_count(self):
        return self.pages.filter(status='published', page_type='post').count()


class Page(models.Model):
    """صفحه/مقاله — هسته CMS"""

    class PageType(models.TextChoices):
        PAGE = 'page', 'صفحه ایستا'
        POST = 'post', 'مقاله / بلاگ'
        GUIDE = 'guide', 'راهنما'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'پیش‌نویس'
        PUBLISHED = 'published', 'منتشرشده'
        ARCHIVED = 'archived', 'آرشیو'

    # اطلاعات اصلی
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True, verbose_name='اسلاگ', blank=True)
    content = models.TextField(verbose_name='محتوا (HTML)', blank=True)
    excerpt = models.TextField(blank=True, verbose_name='خلاصه', help_text='نمایش در لیست مقالات و meta description')
    featured_image = models.ImageField(upload_to='pages/featured/', blank=True, null=True, verbose_name='تصویر شاخص')

    # نوع و دسته‌بندی
    page_type = models.CharField(max_length=10, choices=PageType.choices, default=PageType.PAGE, verbose_name='نوع')
    category = models.ForeignKey(
        PostCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pages', verbose_name='دسته‌بندی',
        help_text='فقط برای مقالات'
    )

    # وضعیت و نویسنده
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT, verbose_name='وضعیت')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pages', verbose_name='نویسنده'
    )

    # نمایش در فهرست
    show_in_header = models.BooleanField(default=False, verbose_name='نمایش در فهرست هدر')
    show_in_footer = models.BooleanField(default=False, verbose_name='نمایش در فهرست فوتر')
    menu_order = models.IntegerField(default=0, verbose_name='ترتیب در فهرست')

    # تاریخ
    publish_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    # آمار
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')

    # SEO
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان SEO', help_text='خالی = عنوان صفحه')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO', help_text='خالی = خلاصه')

    class Meta:
        verbose_name = 'صفحه / مقاله'
        verbose_name_plural = 'صفحات و مقالات'
        ordering = ['-publish_date', '-created_at']
        indexes = [
            models.Index(fields=['status', 'page_type']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f'{self.get_page_type_display()}: {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            counter = 1
            orig = self.slug
            while Page.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{orig}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    @property
    def jalali_publish(self):
        dt = self.publish_date or self.created_at
        if dt:
            return jdatetime.datetime.fromgregorian(datetime=dt).strftime('%d %B %Y')
        return ''

    @property
    def jalali_created(self):
        if self.created_at:
            return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d')
        return ''

    def get_effective_seo_title(self):
        if self.seo_title:
            return self.seo_title
        return f'{self.title} | همیار فرش'

    def get_effective_seo_description(self):
        if self.seo_description:
            return self.seo_description
        if self.excerpt:
            return self.excerpt[:160]
        # Strip HTML tags for auto description
        import re
        text = re.sub(r'<[^>]+>', '', self.content)
        return text[:160] if text else ''

    def get_absolute_url(self):
        if self.page_type == self.PageType.PAGE:
            return f'/page/{self.slug}/'
        return f'/blog/{self.slug}/'

    def get_related_pages(self):
        """صفحات ایستای دیگر (برای سایدبار)"""
        return Page.objects.filter(
            status='published', page_type='page'
        ).exclude(pk=self.pk).order_by('menu_order')[:6]
