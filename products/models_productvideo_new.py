"""
مدل جدید ProductVideo با قابلیت بهینه‌سازی خودکار
این کد باید جایگزین کلاس ProductVideo در models.py شود
"""

class ProductVideo(models.Model):
    """ویدیوهای محصول با بهینه‌سازی خودکار"""
    
    PROCESSING_STATUS = [
        ('pending', 'در صف پردازش'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'خطا در پردازش'),
    ]
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='videos',
        verbose_name='محصول'
    )
    
    # فایل‌های ویدیو
    original_file = models.FileField(
        upload_to='products/videos/originals/',
        verbose_name='ویدیو اصلی'
    )
    video_720p = models.FileField(
        upload_to='products/videos/720p/',
        blank=True, null=True,
        verbose_name='ویدیو 720p'
    )
    video_480p = models.FileField(
        upload_to='products/videos/480p/',
        blank=True, null=True,
        verbose_name='ویدیو 480p'
    )
    thumbnail = models.ImageField(
        upload_to='products/videos/thumbnails/',
        blank=True, null=True,
        verbose_name='تصویر پیش‌نمایش'
    )
    
    # اطلاعات فنی
    duration = models.FloatField(
        null=True, blank=True,
        verbose_name='مدت زمان (ثانیه)'
    )
    original_width = models.IntegerField(
        null=True, blank=True,
        verbose_name='عرض اصلی (پیکسل)'
    )
    original_height = models.IntegerField(
        null=True, blank=True,
        verbose_name='ارتفاع اصلی (پیکسل)'
    )
    original_size = models.BigIntegerField(
        null=True, blank=True,
        verbose_name='حجم اصلی (بایت)'
    )
    size_720p = models.BigIntegerField(
        null=True, blank=True,
        verbose_name='حجم 720p (بایت)'
    )
    size_480p = models.BigIntegerField(
        null=True, blank=True,
        verbose_name='حجم 480p (بایت)'
    )
    
    # وضعیت پردازش
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='pending',
        verbose_name='وضعیت پردازش'
    )
    processing_error = models.TextField(
        blank=True,
        verbose_name='خطای پردازش'
    )
    processing_progress = models.IntegerField(
        default=0,
        verbose_name='درصد پیشرفت پردازش'
    )
    processed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='زمان پردازش'
    )
    
    # متاداده
    title = models.CharField(max_length=200, blank=True, verbose_name='عنوان')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    alt_text = models.CharField(
        max_length=200, blank=True, 
        verbose_name='متن جایگزین (alt)'
    )
    
    # SEO
    seo_title = models.CharField(
        max_length=200, blank=True,
        verbose_name='عنوان SEO ویدیو'
    )
    seo_description = models.TextField(
        blank=True,
        verbose_name='توضیحات SEO ویدیو'
    )
    
    # نمایش
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_featured = models.BooleanField(default=False, verbose_name='ویدیو شاخص')
    show_in_gallery = models.BooleanField(
        default=True,
        verbose_name='نمایش در گالری ویدیو'
    )
    
    # آمار
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'ویدیوی محصول'
        verbose_name_plural = 'ویدیوهای محصولات'
        ordering = ['order', '-uploaded_at']
        indexes = [
            models.Index(fields=['processing_status']),
            models.Index(fields=['show_in_gallery']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f'ویدیو {self.product.name} - {self.get_processing_status_display()}'
    
    def get_effective_title(self):
        """عنوان مؤثر (دستی یا خودکار)"""
        if self.title:
            return self.title
        
        # تولید خودکار
        parts = ['ویدیو', self.product.name]
        if self.product.background_color:
            parts.append(self.product.background_color.name)
        parts.append(f'{self.product.album.comb} شانه')
        
        return ' '.join(parts)
    
    def get_effective_alt(self):
        """متن alt مؤثر"""
        if self.alt_text:
            return self.alt_text
        return self.get_effective_title()
    
    def get_effective_seo_title(self):
        """عنوان SEO مؤثر"""
        if self.seo_title:
            return self.seo_title
        return f'{self.get_effective_title()} | گالری ویدیو همیار فرش'
    
    def get_effective_seo_description(self):
        """توضیحات SEO مؤثر"""
        if self.seo_description:
            return self.seo_description
        
        parts = [
            f'ویدیوی {self.product.name}',
            f'فرش {self.product.album.comb} شانه',
        ]
        
        if self.product.design_type:
            parts.append(f'طرح {self.product.design_type.name}')
        
        if self.description:
            parts.append(self.description[:100])
        
        return '، '.join(parts) + '. مشاهده آنلاین و خرید در همیار فرش.'
    
    def get_duration_display(self):
        """نمایش زمان به صورت mm:ss"""
        if not self.duration:
            return '--:--'
        
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f'{minutes}:{seconds:02d}'
    
    def get_size_reduction_percent(self):
        """درصد کاهش حجم نسبت به اصلی"""
        if not self.original_size or not self.size_480p:
            return None
        
        reduction = (1 - self.size_480p / self.original_size) * 100
        return round(reduction, 1)
    
    def get_best_quality_url(self):
        """انتخاب بهترین کیفیت موجود"""
        if self.video_720p:
            return self.video_720p.url
        elif self.video_480p:
            return self.video_480p.url
        elif self.original_file:
            return self.original_file.url
        return None
    
    def get_mobile_quality_url(self):
        """انتخاب کیفیت مناسب موبایل"""
        if self.video_480p:
            return self.video_480p.url
        elif self.video_720p:
            return self.video_720p.url
        elif self.original_file:
            return self.original_file.url
        return None
    
    def get_similar_videos(self, limit=6):
        """ویدیوهای مشابه بر اساس ویژگی‌های محصول"""
        similar = ProductVideo.objects.filter(
            processing_status='completed',
            show_in_gallery=True
        ).exclude(id=self.id)
        
        # اولویت 1: همان آلبوم
        same_album = similar.filter(product__album=self.product.album)
        
        # اولویت 2: همان نوع طرح
        if self.product.design_type:
            same_design = similar.filter(product__design_type=self.product.design_type)
        else:
            same_design = ProductVideo.objects.none()
        
        # اولویت 3: همان رنگ زمینه
        if self.product.background_color:
            same_color = similar.filter(product__background_color=self.product.background_color)
        else:
            same_color = ProductVideo.objects.none()
        
        # ترکیب با حذف تکراری
        combined = (same_album | same_design | same_color).distinct()
        
        return combined.order_by('-view_count', '-uploaded_at')[:limit]
    
    @property
    def is_ready(self):
        """آیا ویدیو آماده پخش است؟"""
        return self.processing_status == 'completed'
    
    @property
    def jalali_uploaded(self):
        """تاریخ آپلود شمسی"""
        if self.uploaded_at:
            return jdatetime.datetime.fromgregorian(
                datetime=self.uploaded_at
            ).strftime('%Y/%m/%d')
        return ''
