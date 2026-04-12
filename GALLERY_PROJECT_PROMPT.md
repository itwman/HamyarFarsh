# 🎯 PROMPT: ساخت گالری‌های خلاقانه ویدیو و تصویر - همیار فرش

## 📋 معرفی سیستم فعلی

### پروژه: همیار فرش (HamyarFarsh)
**تکنولوژی:** Django 5.1.15 + MySQL (MariaDB) + Bootstrap 5 RTL + XAMPP (Windows)
**مسیر پروژه:** `C:\xampp\htdocs\Hamyarfarsh`
**پورت سرور:** `0.0.0.0:8200`
**زبان اصلی:** فارسی (RTL)

---

## 🏗️ معماری سیستم

### Apps موجود:
1. **products** - مدیریت محصولات فرش
2. **catalog_app** - دسته‌بندی‌ها (Album, BackgroundColor, DesignType, WeaveType, Feature, ColorTone, CarpetSize)
3. **orders** - مدیریت سفارشات
4. **accounts** - احراز هویت کاربران (تلفن‌محور)
5. **dashboard** - پنل مدیریت
6. **customer_panel** - پنل مشتری
7. **shop** - فروشگاه
8. **payments** - پرداخت‌ها
9. **settings_app** - تنظیمات سایت (Solo model)
10. **utils** - ابزارهای کمکی (SMS, VideoProcessor)

---

## 🎬 سیستم بهینه‌سازی ویدیو (تازه پیاده‌سازی شده)

### مدل ProductVideo (آپدیت شده):

```python
class ProductVideo(models.Model):
    # فایل‌های ویدیو
    original_file = models.FileField(upload_to='products/videos/originals/')
    video_720p = models.FileField(upload_to='products/videos/720p/', blank=True, null=True)
    video_480p = models.FileField(upload_to='products/videos/480p/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='products/videos/thumbnails/', blank=True, null=True)
    
    # اطلاعات فنی
    duration = models.FloatField(null=True, blank=True)  # ثانیه
    original_width = models.IntegerField(null=True, blank=True)
    original_height = models.IntegerField(null=True, blank=True)
    original_size = models.BigIntegerField(null=True, blank=True)
    size_720p = models.BigIntegerField(null=True, blank=True)
    size_480p = models.BigIntegerField(null=True, blank=True)
    
    # وضعیت پردازش
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'در صف پردازش'),
            ('processing', 'در حال پردازش'),
            ('completed', 'تکمیل شده'),
            ('failed', 'خطا در پردازش'),
        ],
        default='pending'
    )
    processing_progress = models.IntegerField(default=0)  # 0-100
    processing_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # متاداده
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    
    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    
    # نمایش
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    show_in_gallery = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    # تاریخ
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### ویژگی‌های پردازش ویدیو:
- ✅ پردازش خودکار بعد از آپلود (Signal-based)
- ✅ تبدیل به 720p (برای دسکتاپ)
- ✅ تبدیل به 480p (بهینه موبایل)
- ✅ ساخت thumbnail خودکار
- ✅ استخراج metadata (duration, dimensions, file size)
- ✅ کاهش حجم 60-70%
- ✅ پشتیبانی از ویدیوهای افقی و عمودی
- ✅ نمایش progress bar در admin
- ✅ FFmpeg-based processing

### کلاس VideoProcessor (`utils/video_processor.py`):
- استخراج metadata با `ffmpeg.probe`
- تبدیل کیفیت با حفظ aspect ratio
- ساخت thumbnail از ثانیه اول
- Error handling و logging کامل
- Threading برای پردازش async

---

## 🖼️ سیستم تصاویر محصولات (موجود)

### مدل ProductImage:

```python
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    original = models.ImageField(upload_to='products/originals/')
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True)
    featured_image = models.ImageField(
        upload_to='products/featured/', 
        blank=True, 
        null=True,
        verbose_name='تصویر شاخص 1000×1000'
    )  # ✅ تصاویر مربع با واترمارک
    
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### ویژگی‌های تصاویر:
- ✅ تصاویر اصلی (original)
- ✅ تصاویر شاخص 1000×1000 با واترمارک (featured_image)
- ✅ تصاویر thumbnail
- ✅ alt text خودکار برای SEO

---

## 🎯 درخواست: ساخت دو گالری خلاقانه

### 1️⃣ گالری ویدیو (YouTube/آپارات استایل)

**URL پیشنهادی:** `/gallery/videos/`

**الزامات:**
- 📱 **موبایل First Design** (بیشتر کاربران موبایل دارند)
- 🎬 نمایش تمام ویدیوهای محصولاتی که `show_in_gallery=True` هستند
- 🖼️ کارت‌های ویدیو با thumbnail، عنوان، مدت زمان
- 🔍 فیلترهای هوشمند:
  - رنگ زمینه (background_color)
  - نوع طرح (design_type)
  - شانه (album.comb)
  - نوع بافت (weave_type)
  - ویژگی (feature)
- 🎯 **ویدیوهای مشابه** در صفحه تک ویدیو:
  - بر اساس همان آلبوم
  - بر اساس نوع طرح
  - بر اساس رنگ زمینه
  - الگوریتم: `ProductVideo.get_similar_videos(limit=6)`
- 📊 **اسکیمای ویدیو** برای SEO (Schema.org VideoObject)
- 🛒 دکمه "خرید محصول" با لینک به `product.get_absolute_url()`
- ▶️ پلیر ویدیو با کیفیت‌های مختلف (480p, 720p, original)
- 📈 شمارش بازدید (view_count++)

**ویژگی‌های طراحی:**
- Grid responsive (موبایل: 1 ستون، تبلت: 2 ستون، دسکتاپ: 3-4 ستون)
- Lazy loading برای ویدیوها
- Skeleton loaders
- Infinite scroll یا pagination
- فیلترهای sticky در موبایل
- Swipe gestures برای موبایل

---

### 2️⃣ گالری تصاویر (Pinterest/Google Images استایل)

**URL پیشنهادی:** `/gallery/images/`

**الزامات:**
- 📱 **موبایل First Design**
- 🖼️ نمایش تصاویر `featured_image` (1000×1000 با واترمارک)
- 🎨 **Masonry Grid Layout** (Pinterest استایل)
- 🔍 فیلترهای تعاملی:
  - رنگ زمینه
  - نوع طرح
  - شانه
  - سایز (از CarpetSize)
  - نوع بافت
  - رنج قیمت
- 🔎 **Lightbox** برای نمایش تصویر کامل:
  - نمایش تصویر بزرگ
  - مشخصات محصول (نام، شانه، رنگ، قیمت)
  - دکمه "خرید محصول"
  - دکمه‌های قبلی/بعدی
  - Swipe برای موبایل
  - کلید ESC برای بستن
- 🛍️ لینک مستقیم به صفحه محصول
- 🔄 بارگذاری تدریجی (Infinite scroll)

**ویژگی‌های طراحی:**
- Masonry layout با کتابخانه مناسب (Masonry.js یا Pure CSS Grid)
- تصاویر با aspect ratio ثابت
- Hover effects
- Lazy loading
- Skeleton loaders
- فیلترهای drawer در موبایل
- Search box برای جستجوی سریع

---

## 🎨 الزامات طراحی (خلاقانه و موبایل‌محور)

### رنگ‌بندی و تم:
- استفاده از تم موجود Bootstrap 5 RTL
- رنگ‌های اصلی: مطابق با تنظیمات SiteSettings
- Dark mode optional (اختیاری)

### UI/UX موبایل:
- ✅ Touch-friendly (دکمه‌های بزرگ، حداقل 44×44px)
- ✅ Swipe gestures
- ✅ Pull to refresh
- ✅ Bottom navigation یا Floating Action Button
- ✅ Modal های تمام صفحه در موبایل
- ✅ فونت خوانا (Vazirmatn یا IRANSans)
- ✅ فاصله‌گذاری مناسب

### Performance:
- ✅ Lazy loading
- ✅ Image optimization
- ✅ CDN برای assets استاتیک
- ✅ Caching
- ✅ Pagination یا Infinite scroll

### SEO:
- ✅ Schema.org markup (VideoObject, ImageObject)
- ✅ Meta tags
- ✅ OpenGraph برای اشتراک‌گذاری
- ✅ Sitemap
- ✅ Canonical URLs

---

## 🛠️ فناوری‌های پیشنهادی

### Frontend:
- **Framework:** Bootstrap 5 RTL (موجود)
- **Grid Layout:** CSS Grid یا Masonry.js
- **Video Player:** Video.js یا HTML5 native player
- **Lightbox:** GLightbox یا Fancybox
- **Lazy Load:** Vanilla LazyLoad یا Intersection Observer API
- **Icons:** FontAwesome 6 (موجود)

### Backend:
- **Views:** Class-based views (ListView, DetailView)
- **Filtering:** Django-filter
- **Pagination:** Django Paginator
- **Caching:** Django cache framework
- **SEO:** Django-SEO یا manual implementation

---

## 📂 ساختار URL پیشنهادی

```python
# در apps جدید یا shop/urls.py

urlpatterns = [
    # گالری ویدیو
    path('gallery/videos/', VideoGalleryView.as_view(), name='video_gallery'),
    path('gallery/videos/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    
    # گالری تصاویر
    path('gallery/images/', ImageGalleryView.as_view(), name='image_gallery'),
    
    # API endpoints (اختیاری - برای AJAX filtering)
    path('api/videos/filter/', VideoFilterAPIView.as_view(), name='video_filter_api'),
    path('api/images/filter/', ImageFilterAPIView.as_view(), name='image_filter_api'),
]
```

---

## 📊 مدل‌های مرتبط

### Product:
```python
- name: نام نقشه
- slug: اسلاگ
- album: آلبوم (ForeignKey)
- background_color: رنگ زمینه
- design_type: نوع طرح
- weave_type: نوع بافت
- feature: ویژگی
- status: وضعیت (available, unavailable, exhibition, coming_soon)
- is_featured: محصول ویژه

متدها:
- get_sell_price_12m(): قیمت فروش 12 متری
- get_price_for_size(carpet_size): قیمت برای سایز خاص
- get_effective_seo_title(): عنوان SEO
- get_effective_seo_description(): توضیحات SEO
```

### Album (از catalog_app):
```python
- name: نام آلبوم
- manufacturer: کارخانه سازنده
- comb: شانه (700, 1000, 1200, 1500 و غیره)
- density: تراکم
- yarn_type: جنس نخ
```

### CarpetSize (از catalog_app):
```python
- name: نام سایز
- length: طول (متر)
- width: عرض (متر)
- area: مساحت (متر مربع)
- is_nine_meter: آیا سایز 9 متری است؟
```

---

## 🎯 اولویت‌های پیاده‌سازی

### فاز 1: گالری ویدیو (اولویت بالا)
1. ✅ ساخت VideoGalleryView
2. ✅ طراحی template موبایل‌محور
3. ✅ پیاده‌سازی فیلترها
4. ✅ ساخت VideoDetailView
5. ✅ ویدیوهای مشابه
6. ✅ اسکیمای ویدیو
7. ✅ پلیر ویدیو با کیفیت‌های مختلف

### فاز 2: گالری تصاویر
1. ✅ ساخت ImageGalleryView
2. ✅ Masonry Grid Layout
3. ✅ فیلترهای تعاملی
4. ✅ Lightbox
5. ✅ Lazy loading

### فاز 3: بهینه‌سازی
1. ✅ Performance optimization
2. ✅ SEO enhancement
3. ✅ Analytics integration
4. ✅ Social sharing

---

## 📝 نکات مهم

### ویدیوهای افقی/عمودی:
- سیستم از هر دو جهت پشتیبانی می‌کند
- `aspect ratio` از metadata استخراج می‌شود
- پلیر ویدیو باید responsive باشد
- در grid، از `object-fit: cover` یا `contain` استفاده شود

### واترمارک:
- تصاویر `featured_image` از قبل واترمارک دارند
- ویدیوها فعلاً واترمارک ندارند (آینده: افزودن واترمارک خودکار)

### کاربران موبایل:
- **70-80% کاربران موبایل هستند**
- طراحی باید Mobile First باشد
- تست روی دستگاه‌های واقعی
- سرعت بارگذاری مهم است

---

## 🚀 خروجی مورد انتظار

### کد منبع:
```
Hamyarfarsh/
├── gallery/  (app جدید یا در shop/)
│   ├── views.py
│   │   ├── VideoGalleryView
│   │   ├── VideoDetailView
│   │   └── ImageGalleryView
│   ├── urls.py
│   └── filters.py (اختیاری)
├── templates/
│   └── gallery/
│       ├── video_gallery.html
│       ├── video_detail.html
│       └── image_gallery.html
├── static/
│   ├── css/
│   │   └── gallery.css
│   └── js/
│       └── gallery.js
```

### مستندات:
- راهنمای استفاده
- توضیحات کد
- دستورالعمل توسعه آینده

---

## 🎨 الهام‌بخش (Reference)

**برای گالری ویدیو:**
- آپارات: https://aparat.com
- YouTube Grid View
- Vimeo Gallery

**برای گالری تصاویر:**
- Pinterest: https://pinterest.com
- Google Images
- Unsplash

**اما با:**
- ✅ طراحی منحصر به فرد برای فرش
- ✅ فیلترهای تخصصی صنعت فرش
- ✅ تمرکز بر موبایل
- ✅ فارسی/RTL

---

## ✅ Checklist قبل از شروع

- [x] مدل ProductVideo آپدیت شد
- [x] VideoProcessor پیاده‌سازی شد
- [x] Signals فعال است
- [x] Migration اجرا شد
- [x] FFmpeg نصب است
- [x] تصاویر featured_image موجود است
- [ ] **آماده برای ساخت گالری‌ها!** 🚀

---

## 🎯 هدف نهایی

دو گالری **خلاقانه، زیبا، سریع و موبایل‌محور** که:
1. ✨ تجربه کاربری عالی ارائه دهند
2. 🎬 ویدیوها و تصاویر را جذاب نمایش دهند
3. 🔍 فیلترهای قدرتمند داشته باشند
4. 🛒 فروش را افزایش دهند
5. 📱 روی موبایل عالی کار کنند
6. 🚀 سریع بارگذاری شوند
7. 📊 SEO-friendly باشند

---

**آیا آماده‌اید؟** 🎨🚀

محمدعلی ناظری
مدیر شرکت توسعه هوشمند فرش ایرانیان (ICSD)
تاریخ: 1404/01/20
