from django.db import models
from django.core.cache import cache
from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    """تنظیمات عمومی سایت - مدل Singleton"""

    # --- اطلاعات سایت ---
    site_name = models.CharField(max_length=200, default='همیار فرش', verbose_name='نام سایت')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name='لوگو سایت (PNG)')
    favicon = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name='فاویکون')

    # --- اطلاعات تماس ---
    phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن ثابت')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='موبایل')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='واتساپ')
    telegram_id = models.CharField(max_length=100, blank=True, verbose_name='آی‌دی تلگرام')
    instagram_id = models.CharField(max_length=100, blank=True, verbose_name='آی‌دی اینستاگرام')
    eitaa_id = models.CharField(max_length=100, blank=True, verbose_name='آی‌دی ایتا')
    bale_id = models.CharField(max_length=100, blank=True, verbose_name='آی‌دی بله')
    website_url = models.URLField(blank=True, verbose_name='آدرس سایت')
    address = models.TextField(blank=True, verbose_name='آدرس فیزیکی')

    # --- تنظیمات تصویر ---
    thumbnail_width = models.PositiveIntegerField(default=350, verbose_name='عرض تامبنیل (پیکسل)')
    thumbnail_height = models.PositiveIntegerField(default=350, verbose_name='ارتفاع تامبنیل (پیکسل)')
    featured_image_size = models.PositiveIntegerField(default=1000, verbose_name='سایز تصویر شاخص (پیکسل)')
    info_bar_color = models.CharField(max_length=7, default='#C62828', verbose_name='رنگ نوار اطلاعات تصویر شاخص')
    featured_line1_template = models.CharField(
        max_length=500, blank=True,
        default='نقشه {name} | رنگ {color} | {comb} شانه | تراکم {density}',
        verbose_name='خط ۱ نوار تصویر شاخص',
        help_text='متغیرها: {name}, {color}, {comb}, {density}, {design}, {weave}, {feature}, {company}, {album}'
    )
    featured_line2_template = models.CharField(
        max_length=500, blank=True,
        default='{company} | جنس نخ: {yarn} | {weave}',
        verbose_name='خط ۲ نوار تصویر شاخص',
        help_text='متغیرها: {name}, {color}, {comb}, {density}, {design}, {weave}, {feature}, {company}, {album}, {yarn}'
    )
    featured_line3_template = models.CharField(
        max_length=500, blank=True,
        default='{mobile}  •  {website}',
        verbose_name='خط ۳ نوار تصویر شاخص',
        help_text='متغیرها: {mobile}, {phone}, {website}, {site_name}, {telegram}, {instagram}'
    )

    # --- تنظیمات قیمت‌گذاری ---
    profit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, verbose_name='درصد سود فروش')
    shipping_cost = models.PositiveBigIntegerField(default=0, verbose_name='هزینه حمل و نقل (تومان)')
    rounding_step = models.PositiveBigIntegerField(default=100000, verbose_name='گرد کردن قیمت به بالا (تومان)')

    # --- تنظیمات سفارش ---
    free_shipping_min = models.PositiveBigIntegerField(default=25000000, verbose_name='حداقل مبلغ ارسال رایگان (تومان)')
    deposit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name='درصد بیعانه')
    cancellation_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50.00, verbose_name='درصد جریمه انصراف از بیعانه')

    # --- تنظیمات اقساط (فاز 8.2) ---
    installment_max = models.PositiveBigIntegerField(default=75000000, verbose_name='سقف فروش اقساطی (تومان)')
    check_max_months = models.PositiveIntegerField(default=12, verbose_name='حداکثر ماه‌های چک صیادی')
    beta_max_months = models.PositiveIntegerField(default=18, verbose_name='حداکثر ماه‌های طرح بتا')
    
    # نرخ سود - با نام‌های جدید
    check_monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.50, 
        verbose_name='نرخ سود ماهانه چک صیادی (%)'
    )
    beta_monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.00, 
        verbose_name='نرخ سود ماهانه طرح بتا (%)'
    )
    
    # پیش‌پرداخت الزامی
    check_prepay_required = models.BooleanField(default=False, verbose_name='پیش‌پرداخت چک صیادی الزامی؟')
    beta_prepay_required = models.BooleanField(default=False, verbose_name='پیش‌پرداخت بتا الزامی؟')

    # --- تنظیمات پیامک ---
    sms_enabled = models.BooleanField(default=False, verbose_name='فعال‌سازی ارسال پیامک')
    sms_api_key = models.CharField(max_length=200, blank=True, verbose_name='کلید API سرویس پیامک')
    sms_sender = models.CharField(max_length=20, blank=True, verbose_name='شماره فرستنده')
    sms_on_order = models.BooleanField(default=False, verbose_name='ارسال پیامک هنگام ثبت سفارش')
    sms_on_confirm = models.BooleanField(default=False, verbose_name='ارسال پیامک هنگام تأیید سفارش')
    sms_on_shipped = models.BooleanField(default=False, verbose_name='ارسال پیامک هنگام ارسال سفارش')
    sms_on_delivered = models.BooleanField(default=False, verbose_name='ارسال پیامک هنگام تحویل سفارش')

    # --- تنظیمات SEO ---
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان SEO سایت')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO سایت')
    seo_keywords = models.TextField(blank=True, verbose_name='کلمات کلیدی SEO')
    product_desc_template = models.TextField(
        blank=True, verbose_name='قالب شرح خودکار محصول',
        help_text='متغیرها: {name}, {color}, {comb}, {density}, {yarn}, {design}, {weave}, {price_12m}'
    )

    # --- کد سفارشی Head/Body/Footer (فاز 16) ---
    custom_head_code = models.TextField(
        blank=True, verbose_name='کد سفارشی <head>',
        help_text='گوگل آنالیتیکس، فونت خارجی، CSS اضافی'
    )
    custom_body_start = models.TextField(
        blank=True, verbose_name='کد بعد از <body>',
        help_text='گوگل تگ منیجر (noscript)'
    )
    custom_body_end = models.TextField(
        blank=True, verbose_name='کد قبل از </body>',
        help_text='چت آنلاین، اسکریپت سفارشی'
    )
    custom_footer_code = models.TextField(
        blank=True, verbose_name='کد HTML انتهای فوتر',
        help_text='نماد اعتماد الکترونیکی، ساماندهی'
    )

    # --- رنگ‌بندی (فاز 16) ---
    primary_color = models.CharField(max_length=7, default='#C62828', verbose_name='رنگ اصلی')
    secondary_color = models.CharField(max_length=7, default='#1565C0', verbose_name='رنگ ثانویه')
    header_bg_color = models.CharField(max_length=7, default='#FFFFFF', verbose_name='رنگ پس‌زمینه هدر')
    footer_bg_color = models.CharField(max_length=7, default='#212121', verbose_name='رنگ پس‌زمینه فوتر')

    # --- تنظیمات خبرنامه (فاز 20) ---
    newsletter_enabled = models.BooleanField(default=True, verbose_name='فرم خبرنامه در فوتر فعال باشد؟')
    newsletter_title = models.CharField(max_length=200, default='خبرنامه', verbose_name='عنوان بخش خبرنامه')
    newsletter_text = models.CharField(
        max_length=500, blank=True,
        default='جهت اطلاع از فروش‌های ویژه و تخفیف‌ها شماره موبایل خود را وارد کنید',
        verbose_name='متن توضیحی خبرنامه'
    )
    newsletter_welcome_sms = models.TextField(
        blank=True,
        default='{name} عزیز، خوش آمدید!\nاز عضویت شما در خبرنامه {site_name} متشکریم.\nبرای اطلاع از تخفیف‌ها و محصولات جدید با ما همراه باشید.',
        verbose_name='متن پیامک خوش‌آمدگویی',
        help_text='متغیرها: {name}, {site_name}'
    )

    # --- چت آنلاین (فاز 21) ---
    live_chat_enabled = models.BooleanField(default=True, verbose_name='چت داخلی فعال باشد؟')
    live_chat_external_code = models.TextField(
        blank=True, verbose_name='کد چت خارجی',
        help_text='کد embed سرویس خارجی (Raychat/Goftino/Crisp). اگر پر باشد به‌جای چت داخلی استفاده می‌شود.'
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return self.site_name
