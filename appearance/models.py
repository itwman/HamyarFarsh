"""
فاز 16: مدیریت فهرست‌ها، فوتر و ظاهر سایت
- MenuItem: فهرست هدر/فوتر با زیرمنو
- FooterWidget: ویجت‌های فوتر (لینک/متن/HTML/شبکه اجتماعی/تماس)
"""
from django.db import models


class MenuItem(models.Model):
    """آیتم فهرست — هدر و فوتر با زیرمنو"""

    class Position(models.TextChoices):
        HEADER = 'header', 'فهرست هدر'
        FOOTER = 'footer', 'فهرست فوتر'
        BOTH = 'both', 'هدر و فوتر'

    title = models.CharField(max_length=200, verbose_name='عنوان')
    link = models.CharField(max_length=500, blank=True, verbose_name='لینک',
                            help_text='مثال: /farsh/ یا /page/about-us/ یا https://...')
    icon = models.CharField(max_length=50, blank=True, verbose_name='آیکون Bootstrap',
                            help_text='مثال: bi-house, bi-telephone, bi-cart3')
    position = models.CharField(max_length=10, choices=Position.choices, default=Position.HEADER,
                                verbose_name='موقعیت')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='والد (زیرمنو)')
    order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    target_blank = models.BooleanField(default=False, verbose_name='باز شدن در تب جدید')
    css_class = models.CharField(max_length=100, blank=True, verbose_name='کلاس CSS اضافی')

    class Meta:
        verbose_name = 'آیتم فهرست'
        verbose_name_plural = 'آیتم‌های فهرست'
        ordering = ['position', 'order']

    def __str__(self):
        prefix = '↳ ' if self.parent else ''
        return f'{prefix}{self.title} ({self.get_position_display()})'

    @property
    def active_children(self):
        return self.children.filter(is_active=True).order_by('order')


class FooterWidget(models.Model):
    """ویجت فوتر — ستون‌های پویا"""

    class WidgetType(models.TextChoices):
        LINKS = 'links', 'لیست لینک‌ها'
        TEXT = 'text', 'متن ساده'
        HTML = 'html', 'کد HTML سفارشی'
        SOCIAL = 'social', 'شبکه‌های اجتماعی'
        CONTACT = 'contact', 'اطلاعات تماس'

    title = models.CharField(max_length=200, verbose_name='عنوان ویجت')
    widget_type = models.CharField(max_length=10, choices=WidgetType.choices, verbose_name='نوع')
    content = models.TextField(blank=True, verbose_name='محتوا',
                               help_text='برای «متن»: متن ساده. برای «HTML»: کد HTML (نماد اعتماد، ساماندهی و...)')
    column = models.IntegerField(default=1, verbose_name='ستون (1-4)',
                                 help_text='شماره ستون فوتر از راست')
    order = models.IntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'ویجت فوتر'
        verbose_name_plural = 'ویجت‌های فوتر'
        ordering = ['column', 'order']

    def __str__(self):
        return f'{self.title} (ستون {self.column})'

    def get_footer_links(self):
        """لینک‌های فوتری از MenuItem"""
        return MenuItem.objects.filter(
            is_active=True,
            position__in=['footer', 'both'],
            parent__isnull=True
        ).order_by('order')
