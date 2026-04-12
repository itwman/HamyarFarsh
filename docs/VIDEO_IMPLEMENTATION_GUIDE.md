# ==========================================
# راهنمای کامل پیاده‌سازی سیستم بهینه‌سازی ویدیو
# ==========================================
# پروژه: همیار فرش
# تاریخ: 1404/01/20
# ==========================================

## 🎯 مراحل پیاده‌سازی (به ترتیب)

### مرحله 1: نصب نرم‌افزار و کتابخانه‌ها ✅

```bash
# 1. نصب FFmpeg روی ویندوز
# دانلود از: https://www.gyan.dev/ffmpeg/builds/
# فایل: ffmpeg-release-essentials.zip
# استخراج به: C:\ffmpeg
# اضافه کردن به PATH: C:\ffmpeg\bin

# تست نصب
ffmpeg -version

# 2. نصب کتابخانه‌های پایتون
cd C:\xampp\htdocs\Hamyarfarsh
pip install ffmpeg-python
pip install Pillow

# 3. بررسی نصب
python -c "import ffmpeg; print('FFmpeg-Python OK')"
```

### مرحله 2: بک‌اپ و آپدیت مدل ✅

```bash
# بک‌اپ فایل models.py
copy products\models.py products\models_backup_20260409.py

# حالا باید کلاس ProductVideo رو جایگزین کنید
```

**کد جدید ProductVideo** در فایل `products/models_productvideo_new.py` ذخیره شده.

برای جایگزینی:
1. فایل `products/models.py` رو باز کنید
2. کل کلاس `ProductVideo` (از خط ~340 تا ~360) رو پیدا کنید
3. حذف کنید و محتوای فایل `products/models_productvideo_new.py` رو جایگزین کنید

### مرحله 3: ساخت ماژول VideoProcessor ✅

فایل `utils/video_processor.py` رو ایجاد کنید با محتوای زیر:

```python
"""
پردازشگر خودکار ویدیو - بهینه‌سازی برای پخش آنلاین
"""
import os
import logging
from pathlib import Path
from django.core.files import File
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    logger.warning("ffmpeg-python not installed. Video processing will be disabled.")
    FFMPEG_AVAILABLE = False


class VideoProcessor:
    """کلاس بهینه‌سازی ویدیو"""
    
    def __init__(self, video_instance):
        """
        Args:
            video_instance: نمونه ProductVideo
        """
        self.video = video_instance
        self.original_path = video_instance.original_file.path
        
    def process(self):
        """پردازش کامل ویدیو"""
        if not FFMPEG_AVAILABLE:
            logger.error("FFmpeg not available for video processing")
            self.video.processing_status = 'failed'
            self.video.processing_error = 'FFmpeg not installed'
            self.video.save()
            return False
        
        try:
            logger.info(f"Starting video processing for: {self.video.id}")
            
            self.video.processing_status = 'processing'
            self.video.processing_progress = 0
            self.video.save()
            
            # 1. استخراج اطلاعات
            self.extract_metadata()
            self.video.processing_progress = 20
            self.video.save()
            
            # 2. ساخت thumbnail
            self.generate_thumbnail()
            self.video.processing_progress = 40
            self.video.save()
            
            # 3. تبدیل به 720p
            if self.video.original_height and self.video.original_height > 720:
                self.convert_to_720p()
                self.video.processing_progress = 70
                self.video.save()
            else:
                logger.info("Video is smaller than 720p, skipping 720p conversion")
            
            # 4. تبدیل به 480p
            self.convert_to_480p()
            self.video.processing_progress = 90
            self.video.save()
            
            # تکمیل موفق
            self.video.processing_status = 'completed'
            self.video.processing_progress = 100
            self.video.processed_at = timezone.now()
            self.video.save()
            
            logger.info(f"Video processing completed successfully: {self.video.id}")
            return True
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}", exc_info=True)
            self.video.processing_status = 'failed'
            self.video.processing_error = str(e)
            self.video.save()
            return False
    
    def extract_metadata(self):
        """استخراج اطلاعات ویدیو"""
        try:
            probe = ffmpeg.probe(self.original_path)
            
            # پیدا کردن stream ویدیو
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if video_stream:
                self.video.original_width = int(video_stream.get('width', 0))
                self.video.original_height = int(video_stream.get('height', 0))
            
            # مدت زمان
            if 'duration' in probe['format']:
                self.video.duration = float(probe['format']['duration'])
            
            # حجم فایل
            self.video.original_size = os.path.getsize(self.original_path)
            
            self.video.save()
            logger.info(f"Metadata extracted: {self.video.original_width}x{self.video.original_height}")
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            raise
    
    def generate_thumbnail(self):
        """ساخت تصویر پیش‌نمایش از ثانیه اول"""
        try:
            # مسیر فایل thumbnail
            thumb_filename = f"thumb_{self.video.id}.jpg"
            thumb_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', 'thumbnails',
                thumb_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            
            # استخراج فریم
            (
                ffmpeg
                .input(self.original_path, ss=1)  # ثانیه اول
                .filter('scale', 640, -1)  # عرض 640، ارتفاع متناسب
                .output(thumb_path, vframes=1, format='image2')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
            self.video.thumbnail = relative_path
            self.video.save()
            
            logger.info(f"Thumbnail generated: {thumb_filename}")
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            # Thumbnail اجباری نیست، ادامه می‌دهیم
    
    def convert_to_720p(self):
        """تبدیل به 720p با بهینه‌سازی"""
        try:
            output_filename = f"video_{self.video.id}_720p.mp4"
            output_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', '720p',
                output_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"Converting to 720p: {output_filename}")
            
            # تبدیل با FFmpeg
            (
                ffmpeg
                .input(self.original_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    video_bitrate='2M',
                    acodec='aac',
                    audio_bitrate='128k',
                    vf='scale=-2:720',  # حفظ aspect ratio
                    preset='medium',
                    crf=23,
                    **{'c:v': 'libx264', 'profile:v': 'high', 'level': '4.0'}
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            self.video.video_720p = relative_path
            self.video.size_720p = os.path.getsize(output_path)
            self.video.save()
            
            logger.info(f"720p conversion completed: {output_filename}")
            
        except Exception as e:
            logger.error(f"720p conversion failed: {str(e)}")
            raise
    
    def convert_to_480p(self):
        """تبدیل به 480p - بهینه برای موبایل"""
        try:
            output_filename = f"video_{self.video.id}_480p.mp4"
            output_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', '480p',
                output_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"Converting to 480p: {output_filename}")
            
            # تبدیل با FFmpeg
            (
                ffmpeg
                .input(self.original_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    video_bitrate='1M',
                    acodec='aac',
                    audio_bitrate='96k',
                    vf='scale=-2:480',
                    preset='medium',
                    crf=23,
                    **{'c:v': 'libx264', 'profile:v': 'main', 'level': '3.1'}
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            self.video.video_480p = relative_path
            self.video.size_480p = os.path.getsize(output_path)
            self.video.save()
            
            logger.info(f"480p conversion completed: {output_filename}")
            
        except Exception as e:
            logger.error(f"480p conversion failed: {str(e)}")
            raise


def process_video(video_id):
    """
    تابع کمکی برای پردازش ویدیو
    
    Args:
        video_id: ID ویدیو
        
    Returns:
        bool: موفق/ناموفق
    """
    from products.models import ProductVideo
    
    try:
        video = ProductVideo.objects.get(id=video_id)
        processor = VideoProcessor(video)
        return processor.process()
    except ProductVideo.DoesNotExist:
        logger.error(f"Video {video_id} not found")
        return False
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        return False
```

### مرحله 4: ساخت Signals ✅

فایل `products/signals.py` رو ایجاد کنید:

```python
"""
Signals برای پردازش خودکار ویدیو
"""
import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVideo

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ProductVideo)
def auto_process_video(sender, instance, created, **kwargs):
    """
    پردازش خودکار ویدیو بعد از آپلود
    
    فقط برای ویدیوهای جدید و در صورتی که در وضعیت pending باشند
    """
    if created and instance.original_file and instance.processing_status == 'pending':
        logger.info(f"Triggering automatic processing for video: {instance.id}")
        
        # پردازش در thread جداگانه تا request block نشه
        def process_in_background():
            from utils.video_processor import process_video
            process_video(instance.id)
        
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Background processing started for video: {instance.id}")
```

فایل `products/apps.py` رو آپدیت کنید:

```python
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'محصولات'
    
    def ready(self):
        """فعال‌سازی signals"""
        import products.signals  # ✅ Import signals
```

### مرحله 5: Migration ✅

```bash
cd C:\xampp\htdocs\Hamyarfarsh

# ساخت migration
python manage.py makemigrations products

# بررسی migration
python manage.py showmigrations products

# اجرای migration
python manage.py migrate products

# اگر خطا داد، migration رو به صورت دستی ویرایش کنید
```

### مرحله 6: آپدیت Admin ✅

فایل `products/admin.py` رو آپدیت کنید - قسمت ProductVideo:

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductVideo

@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product', 'title_display', 'thumbnail_preview',
        'duration_display', 'status_badge', 'progress_bar',
        'size_info', 'uploaded_at'
    ]
    list_filter = ['processing_status', 'is_featured', 'show_in_gallery', 'uploaded_at']
    search_fields = ['product__name', 'title', 'description']
    readonly_fields = [
        'duration', 'original_width', 'original_height',
        'original_size', 'size_720p', 'size_480p',
        'processed_at', 'processing_error', 'thumbnail_preview_large'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('product', 'title', 'description', 'alt_text')
        }),
        ('فایل‌ها', {
            'fields': ('original_file', 'video_720p', 'video_480p', 'thumbnail', 'thumbnail_preview_large')
        }),
        ('اطلاعات فنی', {
            'fields': ('duration', 'original_width', 'original_height', 'original_size', 'size_720p', 'size_480p'),
            'classes': ('collapse',)
        }),
        ('پردازش', {
            'fields': ('processing_status', 'processing_progress', 'processing_error', 'processed_at')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('نمایش', {
            'fields': ('order', 'is_featured', 'show_in_gallery', 'view_count')
        }),
    )
    
    def title_display(self, obj):
        return obj.get_effective_title()
    title_display.short_description = 'عنوان'
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit: cover;" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = 'پیش‌نمایش'
    
    def thumbnail_preview_large(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="320" style="max-height: 240px; object-fit: contain;" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview_large.short_description = 'تصویر پیش‌نمایش'
    
    def duration_display(self, obj):
        return obj.get_duration_display()
    duration_display.short_description = 'مدت زمان'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.processing_status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_processing_status_display()
        )
    status_badge.short_description = 'وضعیت'
    
    def progress_bar(self, obj):
        if obj.processing_status == 'processing':
            return format_html(
                '<div style="width: 100px; background: #f0f0f0; border-radius: 3px;"><div style="width: {}%; background: #17a2b8; color: white; text-align: center; border-radius: 3px; font-size: 10px;">{}%</div></div>',
                obj.processing_progress,
                obj.processing_progress
            )
        return '-'
    progress_bar.short_description = 'پیشرفت'
    
    def size_info(self, obj):
        if obj.original_size and obj.size_480p:
            reduction = obj.get_size_reduction_percent()
            if reduction:
                return format_html(
                    '<span style="color: green;">-{:.1f}%</span>',
                    reduction
                )
        return '-'
    size_info.short_description = 'کاهش حجم'
    
    actions = ['reprocess_videos']
    
    def reprocess_videos(self, request, queryset):
        """پردازش مجدد ویدیوهای انتخاب شده"""
        from utils.video_processor import process_video
        import threading
        
        count = 0
        for video in queryset:
            video.processing_status = 'pending'
            video.processing_progress = 0
            video.processing_error = ''
            video.save()
            
            thread = threading.Thread(target=process_video, args=(video.id,))
            thread.daemon = True
            thread.start()
            count += 1
        
        self.message_user(request, f'{count} ویدیو برای پردازش مجدد ارسال شد.')
    reprocess_videos.short_description = 'پردازش مجدد ویدیوهای انتخاب شده'
```

### مرحله 7: تست ✅

```bash
# تست در Django shell
python manage.py shell

>>> from products.models import Product, ProductVideo
>>> from utils.video_processor import VideoProcessor
>>> 
>>> # ساخت یک ویدیوی تست
>>> product = Product.objects.first()
>>> video = ProductVideo.objects.create(
...     product=product,
...     title='تست ویدیو'
... )
>>> 
>>> # آپلود فایل دستی (از طریق admin بهتره)
>>> # یا تست پردازش
>>> processor = VideoProcessor(video)
>>> processor.process()
```

## 📋 Checklist نهایی

- [ ] FFmpeg نصب شد و در PATH قرار گرفت
- [ ] کتابخانه‌های Python نصب شدند
- [ ] مدل ProductVideo آپدیت شد
- [ ] VideoProcessor ساخته شد
- [ ] Signals فعال شد
- [ ] Migration اجرا شد
- [ ] Admin آپدیت شد
- [ ] تست انجام شد

## 🎬 مرحله بعد: گالری ویدیو و تصاویر

بعد از تکمیل این مراحل، من صفحات گالری رو طراحی و پیاده‌سازی می‌کنم:

1. ✅ گالری ویدیو (YouTube استایل) - موبایل first
2. ✅ گالری تصاویر (Pinterest استایل) - موبایل first
3. ✅ اسکیمای ویدیو برای SEO
4. ✅ فیلترهای هوشمند
5. ✅ ویدیوهای مشابه

## 🚨 نکات مهم

1. پردازش ویدیو زمان‌بر است (1-5 دقیقه بسته به حجم)
2. برای سرور Production باید از Celery استفاده کنید
3. فضای دیسک کافی داشته باشید (حداقل 3 برابر حجم ویدیوهای اصلی)
4. Thumbnail برای SEO و تجربه کاربری مهم است

## 📞 پشتیبانی

اگر در هر مرحله مشکلی پیش آمد، لاگ‌ها رو بررسی کنید:
- Django logs
- FFmpeg output
- Processing errors در admin panel
