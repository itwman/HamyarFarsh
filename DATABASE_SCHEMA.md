# همیار فرش - ساختار دیتابیس (DATABASE SCHEMA)

> نسخه: 1.0
> تاریخ: فروردین 1405
> دیتابیس: MySQL (MariaDB 10.4)

---

## accounts app

### User (کاربر سفارشی)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
phone               VARCHAR(11) UNIQUE NOT NULL          -- شماره موبایل (لاگین)
email               VARCHAR(254) NULL
first_name          VARCHAR(150)
last_name           VARCHAR(150)
role                VARCHAR(20) NOT NULL DEFAULT 'customer'  -- admin / staff / customer
is_active           BOOLEAN DEFAULT TRUE
date_joined         DATETIME
last_login          DATETIME NULL
```

### Address (آدرس ارسال)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
user_id             INT FK -> User
province            VARCHAR(50) NOT NULL                 -- استان
city                VARCHAR(50) NOT NULL                 -- شهر
full_address        TEXT NOT NULL                        -- آدرس کامل
postal_code         VARCHAR(10) NULL                     -- کدپستی
phone               VARCHAR(11) NULL                     -- تلفن تماس
is_default          BOOLEAN DEFAULT FALSE
created_at          DATETIME
```

---

## settings app

### SiteSettings (تنظیمات سایت - Singleton)
```
id                  INT PRIMARY KEY DEFAULT 1
site_name           VARCHAR(200) DEFAULT 'همیار فرش'
logo                VARCHAR(500) NULL                    -- مسیر فایل PNG
favicon             VARCHAR(500) NULL

-- اطلاعات تماس
phone               VARCHAR(20)
mobile              VARCHAR(20)
whatsapp            VARCHAR(20) NULL
telegram_id         VARCHAR(100) NULL
instagram_id        VARCHAR(100) NULL
eitaa_id            VARCHAR(100) NULL
bale_id             VARCHAR(100) NULL
website_url         VARCHAR(200)
address             TEXT NULL

-- تنظیمات تصویر
thumbnail_width     INT DEFAULT 350
thumbnail_height    INT DEFAULT 350
featured_image_size INT DEFAULT 1000                     -- سایز تصویر شاخص
info_bar_color      VARCHAR(7) DEFAULT '#C62828'         -- رنگ نوار اطلاعات

-- تنظیمات قیمت‌گذاری
profit_percent      DECIMAL(5,2) DEFAULT 15.00           -- درصد سود فروش
shipping_cost       BIGINT DEFAULT 0                     -- هزینه حمل (تومان)
rounding_step       BIGINT DEFAULT 100000                -- گرد کردن به بالا

-- تنظیمات سفارش
free_shipping_min   BIGINT DEFAULT 25000000              -- حداقل ارسال رایگان
deposit_percent     DECIMAL(5,2) DEFAULT 10.00           -- درصد بیعانه
cancellation_fee    DECIMAL(5,2) DEFAULT 50.00           -- درصد جریمه انصراف از بیعانه

-- تنظیمات اقساط
installment_max     BIGINT DEFAULT 75000000              -- سقف اقساط
check_max_months    INT DEFAULT 12                       -- حداکثر ماه چکی
beta_max_months     INT DEFAULT 18                       -- حداکثر ماه بتا
check_monthly_rate  DECIMAL(5,2) DEFAULT 2.50            -- سود ماهانه چکی ماه‌به‌ماه
check_bimonth_rate  DECIMAL(5,2) DEFAULT 2.70            -- سود ماهانه چکی دوماه‌به‌دوماه
beta_monthly_rate   DECIMAL(5,2) DEFAULT 2.50            -- سود ماهانه بتا
check_prepay_req    BOOLEAN DEFAULT FALSE                -- پیش‌پرداخت چکی الزامی؟
beta_prepay_req     BOOLEAN DEFAULT FALSE                -- پیش‌پرداخت بتا الزامی؟

-- تنظیمات SEO
seo_title           VARCHAR(200) NULL
seo_description     TEXT NULL
seo_keywords        TEXT NULL
product_desc_template TEXT NULL                           -- قالب شرح خودکار محصول

updated_at          DATETIME
```

---

## catalog app

### Manufacturer (شرکت تولیدی)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(200) NOT NULL
slug                VARCHAR(200) UNIQUE NOT NULL
logo                VARCHAR(500) NULL
phone               VARCHAR(20) NULL
website             VARCHAR(200) NULL
description         TEXT NULL
is_active           BOOLEAN DEFAULT TRUE
seo_title           VARCHAR(200) NULL
seo_description     TEXT NULL
created_at          DATETIME
updated_at          DATETIME
```

### Album (آلبوم محصولات)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
manufacturer_id     INT FK -> Manufacturer NOT NULL
name                VARCHAR(200) NOT NULL
slug                VARCHAR(200) UNIQUE NOT NULL
comb                INT NOT NULL                         -- شانه (700/1000/1200/1500)
density             INT NULL                             -- تراکم
yarn_type           VARCHAR(100) NOT NULL                -- جنس نخ (آکرلیک/پلی‌استر/BCF)
weight_class        VARCHAR(20) DEFAULT 'heavy'          -- سبک/سنگین (light/heavy)
-- پرتی 9 متری
nine_m_waste_type   VARCHAR(10) DEFAULT 'fixed'          -- fixed / percent
nine_m_waste_value  DECIMAL(15,2) DEFAULT 0              -- مقدار (تومان یا درصد)
-- قیمت
base_price_12m      BIGINT NULL                          -- قیمت خرید پایه 12 متری (تومان)
is_active           BOOLEAN DEFAULT TRUE
seo_title           VARCHAR(200) NULL
seo_description     TEXT NULL
created_at          DATETIME
updated_at          DATETIME

UNIQUE(manufacturer_id, slug)
```

### BackgroundColor (رنگ زمینه)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(100) NOT NULL UNIQUE         -- کرم/سرمه‌ای/آبی/...
slug                VARCHAR(100) UNIQUE NOT NULL
color_code          VARCHAR(7) NULL                      -- کد رنگ HEX
sort_order          INT DEFAULT 0
```

### DesignType (نوع طرح)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(100) NOT NULL UNIQUE         -- افشان/خشتی/لچک‌ترنج/...
slug                VARCHAR(100) UNIQUE NOT NULL
description         TEXT NULL                            -- توضیح SEO
sort_order          INT DEFAULT 0
```

### WeaveType (نوع بافت)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(100) NOT NULL UNIQUE         -- بافتی / چاپی (کلاریس)
slug                VARCHAR(100) UNIQUE NOT NULL
```

### Feature (ویژگی)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(100) NOT NULL UNIQUE         -- گل‌برجسته / ساده
slug                VARCHAR(100) UNIQUE NOT NULL
```

### ColorTone (تناژ رنگ)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(50) NOT NULL UNIQUE          -- روشن/تیره/گرم/سرد
slug                VARCHAR(50) UNIQUE NOT NULL
```

### CarpetSize (سایز فرش)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(100) NOT NULL                -- مثلاً "12 متری" / "کناره 4×1" / "گرد قطر 3"
length              DECIMAL(5,2) NULL                    -- طول (متر)
width               DECIMAL(5,2) NULL                    -- عرض (متر)
diameter            DECIMAL(5,2) NULL                    -- قطر (برای گرد)
area                DECIMAL(10,4) NOT NULL               -- مساحت (متر مربع)
is_nine_meter       BOOLEAN DEFAULT FALSE                -- آیا 9 متری 3.50×2.50 است؟
default_order_rule  VARCHAR(10) DEFAULT 'any'            -- any (آزاد) / even (فقط زوج)
sort_order          INT DEFAULT 0
is_active           BOOLEAN DEFAULT TRUE
```

---

## products app

### Product (محصول فرش)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
name                VARCHAR(300) NOT NULL                -- نام نقشه
slug                VARCHAR(300) UNIQUE NOT NULL
album_id            INT FK -> Album NOT NULL
background_color_id INT FK -> BackgroundColor NULL
design_type_id      INT FK -> DesignType NULL
weave_type_id       INT FK -> WeaveType NULL
feature_id          INT FK -> Feature NULL
color_tone_id       INT FK -> ColorTone NULL

-- قیمت (NULL = استفاده از قیمت آلبوم)
purchase_price_12m  BIGINT NULL                          -- قیمت خرید 12 متری (override)

-- وضعیت
status              VARCHAR(20) DEFAULT 'available'      -- available/unavailable/exhibition/coming_soon
is_featured         BOOLEAN DEFAULT FALSE                -- محصول ویژه

-- SEO
seo_title           VARCHAR(200) NULL                    -- خودکار اگر خالی
seo_description     TEXT NULL                            -- خودکار اگر خالی
description         TEXT NULL                            -- شرح دستی (اگر خالی: تولید خودکار)
auto_description    TEXT NULL                            -- شرح خودکار تولیدشده

-- آمار
view_count          INT DEFAULT 0
avg_rating          DECIMAL(3,2) DEFAULT 0.00
rating_count        INT DEFAULT 0

created_at          DATETIME
updated_at          DATETIME

INDEX(album_id)
INDEX(status)
INDEX(background_color_id)
INDEX(design_type_id)
INDEX(avg_rating)
```

### ProductSizeRule (قانون سفارش سایز - override)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
product_id          INT FK -> Product NOT NULL
size_id             INT FK -> CarpetSize NOT NULL
order_rule          VARCHAR(10) NOT NULL                 -- any / even
is_available        BOOLEAN DEFAULT TRUE

UNIQUE(product_id, size_id)
```

### ProductImage (تصویر محصول)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
product_id          INT FK -> Product NOT NULL
original            VARCHAR(500) NOT NULL                -- تصویر اصلی (فشرده‌شده ≤1MB)
thumbnail           VARCHAR(500) NULL                    -- تامبنیل 350×350
featured_image      VARCHAR(500) NULL                    -- تصویر شاخص 1000×1000
is_primary          BOOLEAN DEFAULT FALSE                -- تصویر شاخص؟
alt_text            VARCHAR(300) NULL                    -- متن جایگزین SEO (فارسی)
sort_order          INT DEFAULT 0
created_at          DATETIME

INDEX(product_id, is_primary)
INDEX(product_id, sort_order)
```

### ProductVideo (ویدیو محصول)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
product_id          INT FK -> Product NOT NULL
video_file          VARCHAR(500) NOT NULL
title               VARCHAR(200) NULL
sort_order          INT DEFAULT 0
created_at          DATETIME
```

### ProductRating (امتیاز و نظر محصول)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
product_id          INT FK -> Product NOT NULL
user_id             INT FK -> User NOT NULL
rating              TINYINT NOT NULL                     -- 1 تا 5
comment             TEXT NULL                            -- نظر متنی (اختیاری)
status              VARCHAR(20) DEFAULT 'pending'        -- pending / approved / rejected
created_at          DATETIME
updated_at          DATETIME

UNIQUE(product_id, user_id)                              -- هر کاربر یک امتیاز
INDEX(product_id, status)
INDEX(rating)
```

---

## orders app

### Order (سفارش)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
order_number        VARCHAR(20) UNIQUE NOT NULL           -- شماره سفارش یکتا
customer_id         INT FK -> User NOT NULL
address_id          INT FK -> Address NULL

-- مالی
total_amount        BIGINT NOT NULL                       -- جمع کل (تومان)
paid_amount         BIGINT DEFAULT 0                      -- پرداخت‌شده
remaining           BIGINT DEFAULT 0                      -- مانده

-- روش پرداخت
payment_method      VARCHAR(20) NOT NULL                  -- online / deposit / installment_check / installment_beta
deposit_amount      BIGINT NULL                           -- مبلغ بیعانه

-- وضعیت
status              VARCHAR(20) DEFAULT 'pending'
-- pending / reviewing / confirmed / preparing / shipped / delivered / cancelled

-- ارسال
shipping_cost       BIGINT DEFAULT 0
is_free_shipping    BOOLEAN DEFAULT FALSE

-- قیمت ثابت (برای نقدی)
prices_locked       BOOLEAN DEFAULT FALSE

notes               TEXT NULL
created_at          DATETIME                              -- تاریخ ثبت
updated_at          DATETIME

INDEX(customer_id)
INDEX(status)
INDEX(created_at)
```

### OrderItem (آیتم سفارش)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
order_id            INT FK -> Order NOT NULL
product_id          INT FK -> Product NOT NULL
size_id             INT FK -> CarpetSize NULL             -- NULL = سایز سفارشی
quantity            INT NOT NULL DEFAULT 1
unit_price          BIGINT NOT NULL                       -- قیمت واحد در زمان سفارش
total_price         BIGINT NOT NULL                       -- unit_price × quantity

-- سایز سفارشی
custom_length       DECIMAL(5,2) NULL
custom_width        DECIMAL(5,2) NULL
custom_price        BIGINT NULL                           -- قیمت تعیین‌شده توسط مدیر
custom_status       VARCHAR(20) NULL                      -- pending_price / priced / confirmed

INDEX(order_id)
INDEX(product_id)
```

### OrderStatusLog (لاگ تغییر وضعیت)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
order_id            INT FK -> Order NOT NULL
old_status          VARCHAR(20)
new_status          VARCHAR(20) NOT NULL
changed_by_id       INT FK -> User NULL
note                TEXT NULL
created_at          DATETIME
```

---

## payments app

### Payment (پرداخت)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
order_id            INT FK -> Order NOT NULL
amount              BIGINT NOT NULL                       -- مبلغ (تومان)
payment_type        VARCHAR(20) NOT NULL                  -- online / check / beta / deposit
status              VARCHAR(20) DEFAULT 'pending'         -- pending / success / failed / refunded
transaction_id      VARCHAR(100) NULL                     -- شماره تراکنش بانکی
gateway             VARCHAR(50) NULL                      -- zarinpal / saman / ...
description         TEXT NULL
created_at          DATETIME
updated_at          DATETIME

INDEX(order_id)
INDEX(status)
INDEX(transaction_id)
```

### Installment (قسط)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
payment_id          INT FK -> Payment NOT NULL
installment_number  INT NOT NULL                          -- شماره قسط
amount              BIGINT NOT NULL                       -- مبلغ قسط
due_date            DATE NOT NULL                         -- تاریخ سررسید
status              VARCHAR(20) DEFAULT 'pending'         -- pending / paid / overdue
paid_date           DATE NULL
check_number        VARCHAR(50) NULL                      -- شماره چک صیادی
note                TEXT NULL

INDEX(payment_id)
INDEX(due_date)
INDEX(status)
```

---

## sharing app

### Catalog (کاتالوگ اختصاصی)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
title               VARCHAR(200) NULL
unique_code         VARCHAR(50) UNIQUE NOT NULL            -- کد یکتا لینک
created_by_id       INT FK -> User NOT NULL
expires_at          DATETIME NULL                          -- تاریخ انقضا
view_count          INT DEFAULT 0
is_active           BOOLEAN DEFAULT TRUE
created_at          DATETIME
```

### CatalogItem (آیتم کاتالوگ)
```
id                  INT AUTO_INCREMENT PRIMARY KEY
catalog_id          INT FK -> Catalog NOT NULL
product_id          INT FK -> Product NOT NULL
sort_order          INT DEFAULT 0

UNIQUE(catalog_id, product_id)
```

---

## نکات مهم

1. تمام فیلدهای تاریخ در Python با jdatetime نمایش داده می‌شوند (ذخیره Gregorian، نمایش شمسی)
2. تمام مبالغ به تومان ذخیره می‌شوند (BIGINT)
3. تمام slug ها باید UNIQUE و URL-safe باشند
4. ایندکس‌ها روی فیلدهای فیلتر/جستجو/مرتب‌سازی اضافه شدند
5. Soft delete برای محصولات (وضعیت unavailable) به جای حذف فیزیکی
