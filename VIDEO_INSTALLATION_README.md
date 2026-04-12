# 🎬 نصب کامل سیستم بهینه‌سازی ویدیو

## 📋 مراحل نصب (به ترتیب)

### مرحله 1: اضافه کردن FFmpeg به PATH

```bash
# اجرای اسکریپت:
add_ffmpeg_to_path.bat

# یا دستی:
# کنترل پنل > سیستم > تنظیمات پیشرفته > متغیرهای محیطی
# Path > اضافه کردن: C:\ffmpeg\bin
```

**تست:**
```bash
ffmpeg -version
```

---

### مرحله 2: جایگزینی مدل ProductVideo

```bash
# اجرای اسکریپت خودکار:
update_model.bat

# یا با Python:
python update_product_video_model.py
```

**این اسکریپت:**
- ✅ بک‌اپ خودکار از models.py می‌گیرد
- ✅ کلاس ProductVideo قدیمی را پیدا می‌کند
- ✅ با نسخه جدید جایگزین می‌کند
- ✅ تغییرات را بررسی می‌کند

---

### مرحله 3: نصب کتابخانه‌ها

```bash
pip install ffmpeg-python Pillow
```

---

### مرحله 4: Migration

```bash
python manage.py makemigrations products
python manage.py migrate products
```

---

### مرحله 5: ساخت فولدرها

```bash
mkdir media\products\videos\originals
mkdir media\products\videos\720p
mkdir media\products\videos\480p
mkdir media\products\videos\thumbnails
```

---

### مرحله 6: ریستارت سرور

```bash
python manage.py runserver 0.0.0.0:8200
```

---

## 🚀 نصب یک‌کلیکه (All-in-One)

```bash
install_video_full.bat
```

این اسکریپت تمام مراحل بالا را خودکار انجام می‌دهد!

---

## 📁 فایل‌های ایجاد شده

```
Hamyarfarsh/
├── utils/
│   ├── video_processor.py          ✅ پردازشگر ویدیو
│   └── sms.py                       ✅ سیستم SMS
├── products/
│   ├── models.py                    📝 آپدیت شده
│   ├── models_productvideo_new.py   📋 نسخه جدید ProductVideo
│   ├── signals.py                   ✅ سیگنال‌های خودکار
│   └── apps.py                      ✅ فعال‌سازی signals
├── backups/
│   └── models_backup_*.py           💾 بک‌اپ‌های خودکار
├── docs/
│   ├── VIDEO_OPTIMIZATION_PLAN.md
│   └── VIDEO_IMPLEMENTATION_GUIDE.md
├── update_product_video_model.py    🔧 اسکریپت جایگزینی
├── update_model.bat                 🚀 اجرای خودکار
├── add_ffmpeg_to_path.bat           🔧 تنظیم PATH
└── install_video_full.bat           🚀 نصب کامل
```

---

## ✅ Checklist نصب

- [ ] FFmpeg نصب شد (C:\ffmpeg\bin)
- [ ] FFmpeg به PATH اضافه شد
- [ ] مدل ProductVideo جایگزین شد
- [ ] کتابخانه‌ها نصب شدند (ffmpeg-python, Pillow)
- [ ] Migration ساخته و اجرا شد
- [ ] فولدرهای مورد نیاز ساخته شدند
- [ ] سرور ریستارت شد

---

## 🧪 تست سیستم

### 1. تست FFmpeg
```bash
ffmpeg -version
```

### 2. تست کتابخانه‌ها
```bash
python -c "import ffmpeg; print('OK')"
python -c "from PIL import Image; print('OK')"
```

### 3. تست VideoProcessor
```bash
python -c "from utils.video_processor import VideoProcessor; print('OK')"
```

### 4. تست از Django Shell
```python
python manage.py shell

>>> from products.models import ProductVideo
>>> from utils.video_processor import process_video
>>> print("ProductVideo OK")
ProductVideo OK
```

---

## 🎬 استفاده

### آپلود ویدیو از Admin Panel

1. وارد Admin شوید: http://localhost:8200/admin/
2. Products > Product videos > Add product video
3. انتخاب محصول
4. آپلود ویدیو
5. ذخیره

**پردازش خودکار شروع می‌شود!** 🚀

### مشاهده وضعیت پردازش

در لیست ویدیوها می‌توانید ببینید:
- ⏳ در صف پردازش (pending)
- ⚙️ در حال پردازش (processing) + درصد پیشرفت
- ✅ تکمیل شده (completed)
- ❌ خطا (failed)

---

## 🐛 عیب‌یابی

### خطا: FFmpeg not found
```bash
# بررسی PATH
echo %PATH%

# اضافه کردن دستی
set PATH=%PATH%;C:\ffmpeg\bin
```

### خطا: Migration failed
```bash
# حذف migration های قدیمی
python manage.py migrate products zero

# ساخت مجدد
python manage.py makemigrations products
python manage.py migrate products
```

### خطا: Processing failed
```bash
# بررسی لاگ‌ها
python manage.py shell

>>> from products.models import ProductVideo
>>> v = ProductVideo.objects.last()
>>> print(v.processing_error)
```

---

## 📊 فیلدهای جدید ProductVideo

### فایل‌های ویدیو
- `original_file` - ویدیو اصلی
- `video_720p` - نسخه 720p
- `video_480p` - نسخه 480p (موبایل)
- `thumbnail` - تصویر پیش‌نمایش

### اطلاعات فنی
- `duration` - مدت زمان (ثانیه)
- `original_width` - عرض
- `original_height` - ارتفاع
- `original_size` - حجم اصلی
- `size_720p` - حجم 720p
- `size_480p` - حجم 480p

### پردازش
- `processing_status` - وضعیت
- `processing_progress` - درصد پیشرفت
- `processing_error` - خطای پردازش
- `processed_at` - زمان پردازش

### SEO و نمایش
- `seo_title` - عنوان SEO
- `seo_description` - توضیحات SEO
- `show_in_gallery` - نمایش در گالری
- `is_featured` - ویدیو شاخص
- `view_count` - تعداد بازدید

---

## 🎯 مرحله بعد: گالری‌های خلاقانه

بعد از تکمیل نصب، صفحات زیر ساخته می‌شوند:

### 1. گالری ویدیو (YouTube استایل)
- 📱 طراحی موبایل‌ First
- 🎬 کارت‌های ویدیو با thumbnail
- 🔍 فیلتر هوشمند
- 🎯 ویدیوهای مشابه
- 🛒 دکمه خرید

### 2. گالری تصاویر (Pinterest استایل)
- 📱 Masonry Grid
- 🖼️ تصاویر با واترمارک
- 🎨 فیلترهای تعاملی
- 🔎 Lightbox
- 🛍️ لینک به محصول

---

## 📞 پشتیبانی

### لاگ‌ها
```python
# Django logs
tail -f logs/django.log

# Processing errors
# در Admin Panel: Products > Product videos > [ویدیو] > Processing error
```

### گزارش مشکل
اگر مشکلی پیش آمد:
1. لاگ خطا را کپی کنید
2. نسخه FFmpeg را چک کنید: `ffmpeg -version`
3. نسخه Python: `python --version`
4. نسخه کتابخانه‌ها: `pip list | grep ffmpeg`

---

## 🎉 تبریک!

سیستم بهینه‌سازی ویدیو آماده است! 🚀

حالا می‌توانید:
- ✅ ویدیوهای محصولات را آپلود کنید
- ✅ بهینه‌سازی خودکار انجام شود
- ✅ کیفیت‌های مختلف ذخیره شوند
- ✅ حجم 60-70% کاهش یابد
- ✅ تجربه کاربری عالی داشته باشید
