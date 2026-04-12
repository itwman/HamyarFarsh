# سیستم پردازش ویدیو - راهنمای نصب و استفاده

## 📹 قابلیت‌ها

سیستم پردازش ویدیوی همیارفرش به صورت خودکار ویدیوهای آپلودی را بهینه‌سازی می‌کند:

✅ **بررسی کیفیت**: تشخیص رزولوشن، کدک، حجم و مدت زمان  
✅ **کاهش رزولوشن**: تبدیل ویدیوهای بالا به 720p یا 480p  
✅ **فشرده‌سازی**: کاهش حجم با حفظ کیفیت قابل قبول  
✅ **بهینه برای موبایل**: فرمت MP4 با کدک H.264  
✅ **آماده برای استریم**: فلگ `faststart` برای پخش سریع‌تر  

---

## 🔧 نصب FFmpeg

### Windows (توصیه شده)

#### روش 1: دانلود مستقیم
1. از [ffmpeg.org/download.html](https://ffmpeg.org/download.html) وارد بخش Windows شوید
2. لینک **gyan.dev** را انتخاب کنید
3. فایل **ffmpeg-release-essentials.zip** را دانلود کنید
4. محتویات را در `C:\ffmpeg\` استخراج کنید
5. پوشه `C:\ffmpeg\bin` را به PATH سیستم اضافه کنید:
   - کلید Windows + جستجوی "Environment Variables"
   - Edit System Environment Variables → Environment Variables
   - تحت System Variables، Path را انتخاب کنید → Edit
   - New → `C:\ffmpeg\bin` → OK

#### روش 2: Chocolatey
```powershell
choco install ffmpeg
```

#### تست نصب
```cmd
ffmpeg -version
```

اگر خروجی نمایش داد، نصب موفق بوده است! ✅

---

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg -y
ffmpeg -version
```

### macOS
```bash
brew install ffmpeg
ffmpeg -version
```

---

## ⚙️ پیکربندی Django

تنظیمات پردازش ویدیو در `hamyarfarsh/settings.py`:

```python
# مسیر FFmpeg (فقط اگر در PATH نیست)
FFMPEG_PATH = r'C:\ffmpeg\bin\ffmpeg.exe'  # اختیاری

# حداکثر رزولوشن (720 یا 480)
VIDEO_MAX_RESOLUTION = '720'  # توصیه: 720p برای موبایل

# CRF (Constant Rate Factor): 18-28
# کمتر = کیفیت بیشتر + حجم بیشتر
# بیشتر = کیفیت کمتر + حجم کمتر
VIDEO_CRF = 23  # توصیه: 23 (متعادل)

# Preset (سرعت encoding)
VIDEO_PRESET = 'medium'  # توصیه: medium
# گزینه‌ها: ultrafast, veryfast, fast, medium, slow, slower
```

---

## 🚀 نحوه استفاده

### 1. آپلود ویدیو از پنل ادمین Django

```python
# در Admin Panel
Product → Add Product Video
```

### 2. پردازش خودکار

هنگام ذخیره `ProductVideo`، سیگنال `post_save` فعال می‌شود و:
- اطلاعات ویدیو را بررسی می‌کند
- در صورت نیاز، بهینه‌سازی می‌کند:
  - رزولوشن بالاتر از 720p → تبدیل به 720p
  - کدک غیراستاندارد → تبدیل به H.264
  - حجم بالا → فشرده‌سازی
- فایل اصلی را با نسخه بهینه جایگزین می‌کند

### 3. استفاده برنامه‌نویسی

```python
from products.video_processing import VideoProcessor

processor = VideoProcessor()

# بررسی اطلاعات ویدیو
info = processor.get_video_info('/path/to/video.mp4')
print(info)
# {'width': 1920, 'height': 1080, 'duration': 45.5, 'size_mb': 89.2, 'codec': 'h264'}

# بهینه‌سازی دستی
result = processor.optimize_video(
    input_path='/path/to/video.mp4',
    output_path='/path/to/optimized.mp4',
    target_resolution='720'  # یا '480'
)

# ساخت thumbnail
thumb = processor.generate_thumbnail(
    video_path='/path/to/video.mp4',
    time_offset=2.0  # فریم در ثانیه 2
)
```

---

## 📊 پارامترهای بهینه‌سازی

### رزولوشن‌های پیشنهادی:

| رزولوشن | کاربرد | حجم تقریبی (1 دقیقه) |
|---------|--------|---------------------|
| **720p** | موبایل + تبلت | 5-10 MB |
| **480p** | موبایل کم‌حجم | 2-5 MB |
| 1080p | دسکتاپ (پیشنهاد نمی‌شود) | 15-25 MB |

### CRF (کیفیت):

| CRF | کیفیت | حجم | کاربرد |
|-----|--------|------|--------|
| 18-20 | عالی | بالا | ویدیوهای مهم |
| **23** | خوب | متعادل | **توصیه شده** |
| 26-28 | قابل قبول | پایین | فشرده‌سازی بالا |

---

## ⚠️ نکات مهم

### زمان پردازش
- ویدیوی 1 دقیقه‌ای با preset `medium`: ~30-60 ثانیه
- ویدیوی 5 دقیقه‌ای: 3-5 دقیقه
- برای ویدیوهای طولانی، از Celery استفاده کنید (غیرهمزمان)

### محدودیت‌ها
- حداکثر حجم پیش از پردازش: 100 MB (قابل تنظیم)
- حداکثر مدت زمان: 10 دقیقه (timeout)
- فرمت‌های پشتیبانی شده: MP4, AVI, MOV, MKV, FLV, WebM

### توصیه‌های پروداکشن
```python
# TODO: برای محیط پروداکشن
# 1. استفاده از Celery برای پردازش async:
#    @shared_task
#    def process_video_async(video_id):
#        ...

# 2. ذخیره ویدیوها در Object Storage (S3, MinIO)

# 3. استفاده از CDN برای سرویس‌دهی
```

---

## 🐛 عیب‌یابی

### FFmpeg not found
```
ERROR: FFmpeg not found! Please install FFmpeg.
```
**راه‌حل**: 
- Windows: FFmpeg را نصب کنید و به PATH اضافه کنید
- یا مسیر را در settings تنظیم کنید: `FFMPEG_PATH = r'C:\ffmpeg\bin\ffmpeg.exe'`

### Video optimization timeout
```
ERROR: Video optimization timeout (>10 minutes)
```
**راه‌حل**: 
- حجم ویدیو را کاهش دهید (< 100 MB)
- preset را به `faster` یا `veryfast` تغییر دهید

### Permission denied
```
ERROR: Permission denied: output.mp4
```
**راه‌حل**: 
- دسترسی write به پوشه `media/products/videos/` را بررسی کنید

---

## 📝 لاگ‌ها

سیستم از `logging` استفاده می‌کند:

```python
import logging
logger = logging.getLogger(__name__)

# برای مشاهده لاگ‌ها:
# در settings.py:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'products.video_processing': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

## ✅ چک‌لیست نصب

- [ ] FFmpeg نصب شده
- [ ] `ffmpeg -version` کار می‌کند
- [ ] تنظیمات Django تنظیم شده
- [ ] سیگنال `ProductVideo` فعال است
- [ ] دسترسی write به `media/` موجود است
- [ ] یک ویدیو تست آپلود کنید و لاگ‌ها را بررسی کنید

---

## 📚 منابع بیشتر

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [H.264 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/H.264)
- [Understanding CRF](https://slhck.info/video/2017/02/24/crf-guide.html)

---

**نویسنده**: سیستم همیارفرش  
**تاریخ**: فروردین 1404  
**نسخه**: 1.0
