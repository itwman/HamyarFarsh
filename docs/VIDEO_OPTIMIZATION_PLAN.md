# ==========================================
# سیستم بهینه‌سازی خودکار ویدیوهای محصولات
# ==========================================
# پروژه: همیار فرش
# تاریخ: 1404/01/20
# ==========================================

## 🎯 هدف
بهینه‌سازی خودکار ویدیوهای آپلود شده محصولات به کیفیت‌های مختلف (720p, 480p) 
برای پخش بهینه در موبایل و وب

## 📦 نیازمندی‌ها

### 1. نرم‌افزار
- FFmpeg: نصب روی سرور ویندوز
- ffmpeg-python: کتابخانه پایتون

### 2. کتابخانه‌های پایتون
```bash
pip install ffmpeg-python
pip install pillow  # برای thumbnail
```

### 3. فضای دیسک
- ویدیوهای اصلی: بدون محدودیت
- نسخه 720p: ~60% حجم اصلی
- نسخه 480p: ~30% حجم اصلی
- Thumbnail: بسیار کم (چند کیلوبایت)

## 🗂️ ساختار فایل‌ها

```
media/
└── products/
    └── videos/
        ├── originals/          # ویدیوهای اصلی
        │   └── product_123_original.mp4
        ├── 720p/               # نسخه 720p
        │   └── product_123_720p.mp4
        ├── 480p/               # نسخه 480p
        │   └── product_123_480p.mp4
        └── thumbnails/         # تامبنیل‌ها
            └── product_123_thumb.jpg
```

## 🔧 تغییرات مدل

### products/models.py

```python
class ProductVideo(models.Model):
    """ویدیوهای محصول با بهینه‌سازی خودکار"""
    
    PROCESSING_STATUS = [
        ('pending', 'در صف پردازش'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'خطا در پردازش'),
    ]
    
    product = models.ForeignKey(...)
    
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
        verbose_name='عرض اصلی'
    )
    original_height = models.IntegerField(
        null=True, blank=True,
        verbose_name='ارتفاع اصلی'
    )
    original_size = models.BigIntegerField(
        null=True, blank=True,
        verbose_name='حجم اصلی (بایت)'
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
    processed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='زمان پردازش'
    )
    
    # سایر فیلدها...
    title = models.CharField(...)
    order = models.PositiveIntegerField(...)
    uploaded_at = models.DateTimeField(...)
```

## 🛠️ پردازشگر ویدیو

### utils/video_processor.py

```python
import os
import subprocess
import ffmpeg
from PIL import Image
from django.core.files import File
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """کلاس بهینه‌سازی ویدیو"""
    
    def __init__(self, video_instance):
        self.video = video_instance
        self.original_path = video_instance.original_file.path
    
    def process(self):
        """پردازش کامل ویدیو"""
        try:
            self.video.processing_status = 'processing'
            self.video.save()
            
            # 1. استخراج اطلاعات
            self.extract_metadata()
            
            # 2. ساخت thumbnail
            self.generate_thumbnail()
            
            # 3. تبدیل به 720p
            self.convert_to_720p()
            
            # 4. تبدیل به 480p
            self.convert_to_480p()
            
            # تکمیل موفق
            self.video.processing_status = 'completed'
            self.video.processed_at = timezone.now()
            self.video.save()
            
            logger.info(f"Video processed successfully: {self.video.id}")
            return True
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            self.video.processing_status = 'failed'
            self.video.processing_error = str(e)
            self.video.save()
            return False
    
    def extract_metadata(self):
        """استخراج اطلاعات ویدیو"""
        try:
            probe = ffmpeg.probe(self.original_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            self.video.duration = float(probe['format']['duration'])
            self.video.original_width = int(video_info['width'])
            self.video.original_height = int(video_info['height'])
            self.video.original_size = os.path.getsize(self.original_path)
            self.video.save()
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
    
    def generate_thumbnail(self):
        """ساخت تصویر پیش‌نمایش"""
        try:
            # استخراج فریم اول
            thumbnail_path = self.original_path.replace('.mp4', '_thumb.jpg')
            
            (
                ffmpeg
                .input(self.original_path, ss=1)  # ثانیه اول
                .filter('scale', 640, -1)
                .output(thumbnail_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # ذخیره در مدل
            with open(thumbnail_path, 'rb') as f:
                self.video.thumbnail.save(
                    os.path.basename(thumbnail_path),
                    File(f),
                    save=True
                )
            
            # حذف فایل موقت
            os.remove(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
    
    def convert_to_720p(self):
        """تبدیل به 720p"""
        if self.video.original_height <= 720:
            # ویدیو کوچکتر از 720p است
            logger.info("Video is already smaller than 720p, skipping...")
            return
        
        try:
            output_path = self.original_path.replace(
                'originals', '720p'
            ).replace('.mp4', '_720p.mp4')
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
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
                    crf=23
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(
                output_path,
                settings.MEDIA_ROOT
            )
            self.video.video_720p = relative_path
            self.video.save()
            
        except Exception as e:
            logger.error(f"720p conversion failed: {str(e)}")
    
    def convert_to_480p(self):
        """تبدیل به 480p"""
        try:
            output_path = self.original_path.replace(
                'originals', '480p'
            ).replace('.mp4', '_480p.mp4')
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
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
                    crf=23
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(
                output_path,
                settings.MEDIA_ROOT
            )
            self.video.video_480p = relative_path
            self.video.save()
            
        except Exception as e:
            logger.error(f"480p conversion failed: {str(e)}")


def process_video(video_id):
    """تابع کمکی برای پردازش"""
    from products.models import ProductVideo
    
    try:
        video = ProductVideo.objects.get(id=video_id)
        processor = VideoProcessor(video)
        return processor.process()
    except ProductVideo.DoesNotExist:
        logger.error(f"Video {video_id} not found")
        return False
```

## 🔔 Signals

### products/signals.py

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVideo
from utils.video_processor import process_video
import threading


@receiver(post_save, sender=ProductVideo)
def auto_process_video(sender, instance, created, **kwargs):
    """پردازش خودکار بعد از آپلود"""
    if created and instance.original_file:
        # پردازش async (در thread جداگانه)
        thread = threading.Thread(
            target=process_video,
            args=(instance.id,)
        )
        thread.start()
```

### products/apps.py

```python
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'محصولات'
    
    def ready(self):
        import products.signals  # ✅ فعال‌سازی signals
```

## 🎨 رابط کاربری

### Template نمایش ویدیو

```html
<div class="video-player">
    {% if video.processing_status == 'completed' %}
        <video controls poster="{{ video.thumbnail.url }}">
            <!-- انتخاب کیفیت بر اساس دستگاه -->
            {% if video.video_480p %}
                <source src="{{ video.video_480p.url }}" type="video/mp4" label="480p">
            {% endif %}
            {% if video.video_720p %}
                <source src="{{ video.video_720p.url }}" type="video/mp4" label="720p">
            {% endif %}
            <source src="{{ video.original_file.url }}" type="video/mp4" label="Original">
        </video>
    {% elif video.processing_status == 'processing' %}
        <div class="processing-indicator">
            <i class="fas fa-spinner fa-spin"></i>
            در حال پردازش...
        </div>
    {% elif video.processing_status == 'failed' %}
        <div class="error-message">
            خطا در پردازش ویدیو
        </div>
    {% else %}
        <div class="pending-message">
            در صف پردازش...
        </div>
    {% endif %}
</div>
```

## 📊 مدیریت Admin

### products/admin.py

```python
@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'title', 'duration_display',
        'processing_status', 'size_comparison', 'uploaded_at'
    ]
    list_filter = ['processing_status', 'uploaded_at']
    readonly_fields = [
        'duration', 'original_width', 'original_height',
        'original_size', 'processed_at', 'processing_error'
    ]
    
    def duration_display(self, obj):
        if obj.duration:
            minutes = int(obj.duration // 60)
            seconds = int(obj.duration % 60)
            return f"{minutes}:{seconds:02d}"
        return "-"
    duration_display.short_description = 'مدت زمان'
    
    def size_comparison(self, obj):
        if obj.original_size and obj.video_480p:
            try:
                size_480p = obj.video_480p.size
                reduction = (1 - size_480p / obj.original_size) * 100
                return f"-{reduction:.1f}%"
            except:
                return "-"
        return "-"
    size_comparison.short_description = 'کاهش حجم'
```

## ⚙️ تنظیمات

### settings.py

```python
# تنظیمات ویدیو
VIDEO_PROCESSING = {
    '720p': {
        'height': 720,
        'video_bitrate': '2M',
        'audio_bitrate': '128k',
    },
    '480p': {
        'height': 480,
        'video_bitrate': '1M',
        'audio_bitrate': '96k',
    },
    'preset': 'medium',  # ultrafast, fast, medium, slow
    'crf': 23,  # 0-51, پایین‌تر = کیفیت بهتر
}

# حداکثر حجم آپلود (100MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
```

## 🚀 نصب و راه‌اندازی

### 1. نصب FFmpeg روی ویندوز

```powershell
# دانلود از: https://www.gyan.dev/ffmpeg/builds/
# استخراج و اضافه کردن به PATH
```

### 2. نصب کتابخانه‌ها

```bash
pip install ffmpeg-python pillow
```

### 3. Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. تست

```python
# در Django shell
from products.models import ProductVideo
from utils.video_processor import VideoProcessor

video = ProductVideo.objects.first()
processor = VideoProcessor(video)
processor.process()
```

## 📈 بهبودهای آینده

1. **Celery Task Queue**: پردازش async واقعی
2. **Progress Bar**: نمایش درصد پیشرفت
3. **Multiple Quality**: اضافه کردن 1080p, 360p
4. **Adaptive Streaming**: HLS/DASH
5. **Cloud Processing**: استفاده از سرویس‌های ابری
6. **Watermark**: افزودن واترمارک خودکار

## 🐛 عیب‌یابی

### خطا: FFmpeg not found
```bash
# بررسی نصب
ffmpeg -version

# اضافه کردن به PATH
```

### خطا: Permission denied
```python
# اطمینان از دسترسی به فولدر media
os.chmod('media/products/videos', 0o755)
```

### پردازش کند
```python
# استفاده از preset سریع‌تر
'preset': 'ultrafast'  # به جای 'medium'
```

## 📝 نتیجه‌گیری

با این سیستم:
✅ ویدیوها خودکار بهینه می‌شوند
✅ حجم 60-70% کاهش می‌یابد
✅ کیفیت مناسب موبایل حفظ می‌شود
✅ تجربه کاربری بهتر
✅ مصرف پهنای باند کمتر
