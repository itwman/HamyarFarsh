# 🎯 فاز 9: پنل مدیریت محصولات - راهنمای کامل

## 📦 فایل‌های ایجاد شده

### بک‌اند (3 فایل)
1. ✅ `products/views.py` - Views پنل مدیریت
2. ✅ `products/urls.py` - URL patterns
3. ✅ `products/forms.py` - موجود از قبل

### فرانت‌اند (6 تمپلیت)
4. ✅ `templates/products/product_list.html` - لیست محصولات
5. ✅ `templates/products/product_form.html` - فرم افزودن/ویرایش
6. ✅ `templates/products/product_images.html` - مدیریت تصاویر
7. ✅ `templates/products/product_size_rules.html` - قوانین سایز
8. ✅ `templates/products/product_delete_confirm.html` - تأیید حذف
9. ✅ `templates/products/bulk_price_update.html` - بروزرسانی انبوه

---

## 🔧 مراحل نصب

### 1️⃣ کپی فایل‌ها

```
C:\xampp\htdocs\Hamyarfarsh\
├── products\
│   ├── views.py          ← جایگزین شود
│   └── urls.py           ← جایگزین شود
│
└── templates\products\
    ├── product_list.html
    ├── product_form.html
    ├── product_images.html
    ├── product_size_rules.html
    ├── product_delete_confirm.html
    └── bulk_price_update.html
```

### 2️⃣ نصب کتابخانه Pillow (برای پردازش تصاویر)

```bash
pip install Pillow
```

### 3️⃣ تنظیمات `urls.py` اصلی

باز کنید: `C:\xampp\htdocs\Hamyarfarsh\hamyarfarsh\urls.py`

اضافه کنید:

```python
urlpatterns = [
    # ...
    path('admin-products/', include('products.urls')),  # پنل مدیریت محصولات
    # ...
]
```

### 4️⃣ ایجاد پوشه‌های رسانه

```bash
mkdir C:\xampp\htdocs\Hamyarfarsh\media\products\originals
mkdir C:\xampp\htdocs\Hamyarfarsh\media\products\thumbnails
mkdir C:\xampp\htdocs\Hamyarfarsh\media\products\featured
```

### 5️⃣ تنظیمات رسانه در `settings.py`

بررسی کنید که این تنظیمات وجود داشته باشد:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

و در `urls.py` اصلی (حالت دیباگ):

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 6️⃣ ریستارت سرور

```bash
python manage.py runserver 0.0.0.0:8200
```

---

## 🎓 نحوه استفاده

### دسترسی به پنل

```
http://localhost:8200/admin-products/
```

**نکته:** فقط برای کاربران staff قابل دسترسی است (`@staff_member_required`)

---

## 📋 قابلیت‌های پیاده‌سازی شده

### 1. لیست محصولات (`/admin-products/`)
✅ نمایش جدولی با تصویر، نام، آلبوم، شانه، رنگ، قیمت، وضعیت  
✅ فیلتر پیشرفته: جستجو، شرکت، آلبوم، شانه، وضعیت، رنگ، طرح  
✅ صفحه‌بندی 30 تایی  
✅ شمارش تعداد تصاویر هر محصول  
✅ دکمه‌های سریع: ویرایش، تصاویر، قوانین سایز، مشاهده، حذف  

### 2. افزودن محصول (`/admin-products/add/`)
✅ فرم کامل با تمام فیلدها  
✅ فیلتر آلبوم بر اساس شرکت (JavaScript)  
✅ دسته‌بندی‌ها: رنگ زمینه، نوع طرح، نوع بافت، ویژگی، تناژ  
✅ قیمت خرید اختیاری (override از آلبوم)  
✅ تنظیمات SEO: عنوان، توضیحات، شرح  
✅ پس از ذخیره → هدایت به صفحه آپلود تصاویر  

### 3. ویرایش محصول (`/admin-products/<id>/edit/`)
✅ همان فرم افزودن با داده‌های موجود  
✅ بروزرسانی اطلاعات  

### 4. مدیریت تصاویر (`/admin-products/<id>/images/`)
✅ **آپلود گروهی:** چند تصویر همزمان  
✅ **آپلود تکی:** با تنظیمات دستی (alt text, order, is_primary)  
✅ تولید خودکار تامبنیل و تصویر شاخص (با Pillow)  
✅ نمایش گالری با نشانگر تصویر شاخص (قاب قرمز)  
✅ تنظیم تصویر شاخص با یک کلیک  
✅ حذف تصویر (با حذف فایل‌ها از دیسک)  
✅ مودال نمایش تصویر بزرگ  

### 5. قوانین سایز (`/admin-products/<id>/size-rules/`)
✅ جدول تمام سایزهای فعال  
✅ نمایش قانون پیش‌فرض هر سایز  
✅ امکان تنظیم قانون سفارشی برای هر سایز: آزاد یا فقط زوج  
✅ هایلایت سایزهایی با قانون سفارشی (زرد)  
✅ ذخیره یا حذف قوانین سفارشی  

### 6. بروزرسانی انبوه قیمت (`/admin-products/bulk-price-update/`)
✅ لیست تمام آلبوم‌ها با قیمت فعلی  
✅ انتخاب آلبوم و تغییر قیمت پایه  
✅ نمایش قیمت فعلی به محض انتخاب آلبوم (JavaScript)  
✅ شمارش تعداد محصولات تأثیرگرفته  
✅ پیام موفقیت با جزئیات  

### 7. حذف محصول (`/admin-products/<id>/delete/`)
✅ صفحه تأیید با هشدار  
✅ نمایش اطلاعات محصول  
✅ حذف CASCADE: تصاویر، نظرات، قوانین  

---

## 🎨 ویژگی‌های طراحی

✅ **طراحی RTL** کامل فارسی  
✅ **رنگ‌بندی HamyarFarsh:** قرمز اصلی، خاکستری روشن  
✅ **آیکون‌های Bootstrap Icons** در همه جا  
✅ **کارت‌های hf-card** با سایه ملایم  
✅ **جداول Responsive** با scroll افقی  
✅ **Badge های رنگی** برای وضعیت‌ها  
✅ **دکمه‌های گروهی** برای عملیات سریع  
✅ **Breadcrumb** در صفحات داخلی  
✅ **صفحه‌بندی** استاندارد Django  

---

## 🔐 امنیت

✅ همه view ها با `@staff_member_required` محافظت شده‌اند  
✅ CSRF token در تمام فرم‌ها  
✅ تأیید حذف (confirm modal/page)  
✅ Validation در سمت سرور (Django Forms)  

---

## 📊 پردازش تصاویر

### تابع `generate_thumbnails()`

برای هر تصویر آپلودی:

1. **تامبنیل** (اندازه از تنظیمات سایت):
   - پیش‌فرض: 350×350 پیکسل
   - حفظ نسبت تصویر
   - کیفیت 85%

2. **تصویر شاخص** (مربع):
   - پیش‌فرض: 1000×1000 پیکسل
   - Crop به مربع (از وسط)
   - کیفیت 90%

3. **تبدیل RGBA → RGB:**
   - با پس‌زمینه سفید
   - سازگار با JPEG

---

## ⚠️ نکات مهم

### 1. دسترسی Staff
فقط کاربران با `is_staff=True` می‌توانند وارد پنل شوند.

برای دادن دسترسی staff به یک کاربر:

```bash
python manage.py shell
```

```python
from accounts.models import CustomUser
user = CustomUser.objects.get(phone='09123456789')
user.is_staff = True
user.save()
```

### 2. مسیر رسانه
اطمینان حاصل کنید که Django به پوشه `media` دسترسی خواندن/نوشتن دارد.

### 3. Pillow
بدون Pillow، آپلود تصویر کار نمی‌کند. حتماً نصب کنید:

```bash
pip install Pillow
```

### 4. حجم فایل
برای آپلود تصاویر بزرگ، ممکن است نیاز به تنظیم `DATA_UPLOAD_MAX_MEMORY_SIZE` در `settings.py` باشد:

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
```

---

## 🎯 تست کارکرد

### 1. لیست محصولات
- [ ] صفحه لود می‌شود
- [ ] فیلترها کار می‌کنند
- [ ] صفحه‌بندی کار می‌کند
- [ ] دکمه‌ها کلیک می‌شوند

### 2. افزودن محصول
- [ ] فرم نمایش داده می‌شود
- [ ] ذخیره موفق
- [ ] هدایت به صفحه تصاویر

### 3. آپلود تصویر
- [ ] آپلود تکی کار می‌کند
- [ ] آپلود چندتایی کار می‌کند
- [ ] تامبنیل تولید می‌شود
- [ ] تصویر شاخص تنظیم می‌شود

### 4. قوانین سایز
- [ ] لیست سایزها نمایش داده می‌شود
- [ ] تغییر قانون ذخیره می‌شود
- [ ] قوانین سفارشی هایلایت می‌شوند

### 5. بروزرسانی قیمت
- [ ] انتخاب آلبوم کار می‌کند
- [ ] قیمت فعلی نمایش داده می‌شود
- [ ] تغییر قیمت اعمال می‌شود

---

## 🎉 فاز 9 کامل شد!

تمامی قابلیت‌های پنل مدیریت محصولات پیاده‌سازی شد:
- ✅ لیست و فیلتر پیشرفته
- ✅ افزودن/ویرایش محصول
- ✅ آپلود تصاویر (تک و گروهی)
- ✅ مدیریت قوانین سایز
- ✅ بروزرسانی انبوه قیمت
- ✅ حذف با تأیید
- ✅ پردازش خودکار تصاویر

---

**آماده برای فاز 10!** 🚀
