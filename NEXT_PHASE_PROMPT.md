# پرامپت ادامه پروژه همیار فرش - فاز 7 به بعد

## دستورالعمل
این پروژه "همیار فرش" (HamyarFarsh) یک سیستم مدیریت و فروش فرش ماشینی با Django 5 است.
فازهای 1 تا 6 تکمیل شدند. لطفاً فاز 7 (سبد خرید و سفارش‌گیری) را شروع و تکمیل کن.
تمامی فایل‌ها در مسیر `C:\xampp\htdocs\Hamyarfarsh` هستند و دسترسی کامل داری.
فایل PHASES.md در ریشه پروژه شامل فازبندی کامل ۱۳ فازی و تمام فرمول‌ها و قوانین کسب‌وکار است. حتماً آن را بخوان.

---

## مشخصات فنی کلیدی
- **Django 5.1** + **MySQL (MariaDB 10.4)** با patch سازگاری در settings.py
- **Bootstrap 5 RTL** + **Vazirmatn FD** (همه لوکال، بدون CDN - اینترنت ایران CDN ها بلاک شدند)
- **تقویم شمسی**: jdatetime (ذخیره Gregorian، نمایش شمسی)
- **قالب رنگی**: قرمز دیجی‌کالایی (#C62828)
- **فونت فارسی**: Vazirmatn FD (ارقام فارسی) - فایل‌های woff2 و ttf لوکال
- **پردازش تصویر**: Pillow + arabic_reshaper + python-bidi
- **SEO**: JSON-LD Schema.org, Open Graph, Canonical URLs
- **پورت سرور**: 8200
- **Django 5 + MariaDB 10.4**: نیاز به patch دارد (قبلاً اعمال شده - ببین settings.py)
- **Django 5 MultiFileInput**: کلاس `MultiFileInput` سفارشی در `products/forms.py` ساخته شده (Django 5 ویجت‌های استاندارد رو با multiple ساپورت نمی‌کنه)
- **Unicode slugs**: URL pattern ها باید با `re_path` و `[\w\-]+` باشن (نه `<slug:slug>`) چون slug ها فارسی هستند

---

## ساختار فعلی پروژه

```
C:\xampp\htdocs\Hamyarfarsh\
├── hamyarfarsh/          # پروژه اصلی Django (settings, urls, wsgi)
├── accounts/             # اپ کاربران (User با phone login, Address, نقش‌ها: admin/staff/customer)
├── settings_app/         # تنظیمات سایت (SiteSettings singleton - 40+ فیلد)
├── catalog/              # شرکت‌ها (Manufacturer), آلبوم‌ها (Album), دسته‌بندی‌ها, سایزها
├── products/             # محصولات (Product), تصاویر, ویدیو, امتیاز, قیمت‌گذاری
├── shop/                 # ویترین مشتری (کاتالوگ, جزئیات محصول, فیلتر, امتیاز)
├── orders/               # ← خالی - فاز 7
├── payments/             # ← خالی - فاز 8
├── sharing/              # ← خالی - فاز 11
├── templates/            # base.html + accounts/ + catalog/ + products/ + shop/ + settings_app/
├── static/css,js,fonts,images/  # Bootstrap RTL + Vazirmatn + Chart.js (همه لوکال)
├── media/                # آپلودها
├── PHASES.md             # فازبندی کامل 13 فازی (حتماً بخوان!)
└── DATABASE_SCHEMA.md    # ساختار دیتابیس
```

---

## فازهای تکمیل‌شده

### فاز 1 ✅ زیرساخت
- Django project, MySQL config, MariaDB 10.4 patch
- Base template (base.html) با تم قرمز، ناوبار، فوتر، SEO blocks
- User model (phone login), roles (admin/staff/customer), login/register/profile
- SiteSettings singleton (قیمت‌گذاری، اقساط، SEO، تصویر، تماس)
- jalali_tags templatetag

### فاز 2 ✅ شرکت‌ها و آلبوم‌ها
- Manufacturer (CRUD + slug)
- Album (شانه, تراکم, جنس نخ, وزن, پرتی 9 متری ثابت/درصدی, قیمت پایه 12 متری)

### فاز 3 ✅ دسته‌بندی‌ها
- BackgroundColor, DesignType, WeaveType, Feature, ColorTone
- CarpetSize (17 سایز استاندارد با مساحت محاسباتی و قانون زوج/آزاد)
- Data migration با مقادیر پیش‌فرض

### فاز 4 ✅ مدیریت محصولات
- Product model با قیمت‌گذاری کامل:
  - قیمت فروش 12م = CEIL((خرید × 1.15) + حمل, 100000)
  - سایر سایزها = قیمت_12م ÷ 12 × مساحت
  - 9 متری = (قیمت_12م ÷ 12 × 9) + پرتی (ثابت یا درصدی)
- ProductSizeRule (override قانون سفارش زوج/آزاد)
- ProductImage, ProductVideo, ProductRating
- SEO خودکار (title, description, شرح محصول)
- فرم‌ها: ProductForm, MultiImageUploadForm (کلاس سفارشی), ProductFilterForm
- Views: لیست با فیلتر/صفحه‌بندی، ایجاد، ویرایش، تصاویر، قیمت‌ها، تغییر وضعیت گروهی
- Templates: product_list, product_form, product_images, product_prices

### فاز 5 ✅ سیستم تصاویر
- image_utils.py: compress_image (≤1MB), generate_thumbnail (350×350), generate_featured_image (1000×1000 با لوگو + نوار اطلاعات قرمز)
- signals.py: پردازش خودکار بعد از آپلود (فشرده‌سازی + تامبنیل + تصویر شاخص)
- فونت فارسی Vazirmatn با arabic_reshaper + python-bidi

### فاز 6 ✅ ویترین مشتری + SEO
- shop app: کاتالوگ با فیلتر پیشرفته (شانه/رنگ/طرح/شرکت/بافت/ویژگی + مرتب‌سازی)
- صفحه جزئیات محصول: گالری + مشخصات + جدول قیمت + شرایط خرید + نظرات + محصولات مشابه
- SEO کامل: JSON-LD Product + AggregateRating + Review + BreadcrumbList + Open Graph
- سیستم امتیازدهی ستاره‌ای (1-5) با تأیید مدیر
- فرم سفارش سایز خاص
- URL‌های SEO-friendly: /farsh/, /farsh/<slug>/, /farsh/rang/<slug>/, /farsh/tarh/<slug>/, /farsh/shaane/<int>/
- price_tags templatetag (toman, price_comma, star_range)
- نکته: URL ها با re_path و [\w\-]+ هستند (slug فارسی)

---

## INSTALLED_APPS فعلی
```python
'accounts.apps.AccountsConfig',
'settings_app.apps.SettingsAppConfig',
'catalog.apps.CatalogConfig',
'products.apps.ProductsConfig',
'shop.apps.ShopConfig',
```

## URLs اصلی فعلی
```python
path('admin/', admin.site.urls),
path('accounts/', include('accounts.urls')),
path('settings/', include('settings_app.urls')),
path('catalog/', include('catalog.urls')),
path('products/', include('products.urls')),
path('farsh/', include('shop.urls')),
path('', include('accounts.urls_home')),
```

---

## فرمول‌های کلیدی (از PHASES.md)

### قیمت فروش
```
قیمت_فروش_12م = CEIL((قیمت_خرید × 1.15) + هزینه_حمل, 100000)
سایر سایزها = (قیمت_12م ÷ 12) × مساحت
9 متری ثابت = (قیمت_12م ÷ 12 × 9) + عدد_پرتی
9 متری درصدی = (قیمت_12م ÷ 12 × 9) × (1 + درصد_پرتی/100)
```

### اقساط
```
مانده = جمع_فاکتور - پیش‌پرداخت
سود_کل = درصد_سود_ماهانه × تعداد_ماه
مبلغ_با_سود = مانده × (1 + سود_کل)
مبلغ_هر_قسط = مبلغ_با_سود ÷ تعداد_اقساط
```

### قوانین سفارش
1. ارسال رایگان: فقط نقدی آنلاین کامل + 25+ میلیون
2. بیعانه: حداقل 10% مبلغ کل
3. قیمت روز: برای پرداخت موقع تحویل (بیعانه ثابت)
4. انصراف: 50% بیعانه + ایاب‌ذهاب
5. سایز خاص: فقط تسویه کامل
6. سفارش زوجی: سایزهای 9مربع/15/24/کناره/قالیچه/پادری/گرد پیش‌فرض زوج
7. اقساطی: سقف 75 میلیون، مابقی نقدی
8. چکی: حداکثر 12 ماه (ماهانه 2.5% / دوماهانه 2.7%)
9. بتا: حداکثر 18 ماه (بازنشستگان بانک رفاه)

---

## فاز 7: سبد خرید و سفارش‌گیری (باید الان ساخته بشه)

### 7.1 سبد خرید
- افزودن به سبد با انتخاب سایز/تعداد
- کنترل قانون زوج/فرد هنگام افزودن
- ویرایش تعداد، حذف آیتم
- محاسبه جمع کل آنی

### 7.2 فرآیند ثبت سفارش
- انتخاب روش پرداخت: نقدی آنلاین / بیعانه+موقع تحویل / اقساطی (چکی/بتا)
- اطلاعات ارسال (انتخاب آدرس)
- شرایط ارسال رایگان: نقدی + 25+ میلیون
- هشدارها: قیمت روز، جریمه انصراف، سایز خاص

### 7.3 مدل سفارش
- Order: مشتری، وضعیت، روش پرداخت، مبلغ کل، بیعانه، آدرس ارسال
- OrderItem: سفارش، محصول، سایز، تعداد، قیمت واحد، سایز سفارشی
- OrderStatusLog: لاگ تغییر وضعیت
- وضعیت‌ها: pending/reviewing/confirmed/preparing/shipped/delivered/cancelled

### نکات مهم پیاده‌سازی
- اپ orders خالیه، باید __init__.py, apps.py, models.py, views.py, urls.py, forms.py, admin.py ساخته بشه
- templates/orders/ هم باید ساخته بشه
- باید به INSTALLED_APPS و urls.py اصلی اضافه بشه
- تاریخ‌ها شمسی (jdatetime)
- مبالغ به تومان (BigInteger)
- سبد خرید: session-based (برای کاربران بدون لاگین هم کار کنه)

---

## نکات فنی حیاتی
1. **MariaDB 10.4 patch**: در settings.py قبلاً اعمال شده - دست نزن
2. **CDN ممنوع**: تمامی فایل‌های JS/CSS/Font باید لوکال باشن
3. **Unicode slug**: از `re_path(r'^(?P<slug>[\w\-]+)/$', ...)` استفاده کن (نه path با slug)
4. **Django 5 FileInput**: برای آپلود چندتایی از `MultiFileInput` سفارشی استفاده کن (ببین products/forms.py)
5. **فونت**: Vazirmatn FD (ارقام فارسی) - فایل‌های woff2 در static/fonts/vazirmatn/
6. **تمام widgets** کلاس `form-control` یا `form-select` Bootstrap بگیرن
7. **تمام templates** از base.html ارث ببرن و بلوک‌های SEO رو پر کنن
