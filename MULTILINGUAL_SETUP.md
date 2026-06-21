# چندزبانه‌سازی همیار فرش — راهنما و نقشه راه

معماری: **یک کدبیس، یک دیتابیس، چند ساب‌دامین**. زبان از روی ساب‌دامین تشخیص داده می‌شود.

زبان‌ها (۹ تا): فارسی (پیش‌فرض)، عربی، اردو، انگلیسی، روسی، اسپانیایی، فرانسوی، آلمانی، هندی.
نگاشت ساب‌دامین → زبان:

| ساب‌دامین | زبان | جهت |
|---|---|---|
| hamyarfarsh.ir / www | fa | RTL |
| ar.hamyarfarsh.ir | عربی | RTL |
| ur.hamyarfarsh.ir | اردو | RTL |
| en / ru / es / fr / de / hi .hamyarfarsh.ir | همان زبان | LTR |

---

## ✅ فاز ۱ — انجام شد (زیرساخت i18n + ساب‌دامین)

تغییرات اعمال‌شده در کد:

1. `hamyarfarsh/settings.py`
   - تعریف `LANGUAGES` با ۹ زبان، `LOCALE_PATHS`، تنظیمات کوکی زبان.
   - افزودن `SubdomainLocaleMiddleware` به `MIDDLEWARE` (بعد از Session، قبل از Common).
   - افزودن `django.template.context_processors.i18n` به قالب‌ها.
   - افزودن `https://*.hamyarfarsh.ir` به `CSRF_TRUSTED_ORIGINS`.
2. `hamyarfarsh/middleware.py` (جدید) — تشخیص زبان از ساب‌دامین با fallback به فارسی. ۱۶ سناریو تست و تأیید شد.
3. `templates/base.html` — تگ `<html lang dir>` داینامیک شد (RTL/LTR خودکار).
4. `templates/includes/language_switcher.html` (جدید) — سوییچر زبان مبتنی بر ساب‌دامین.
5. پوشه `locale/` ساخته شد.

> در این فاز فقط زیرساخت اضافه شده و رفتار سایت فارسی تغییری نکرده است.

---

## کارهای لازم برای فعال‌سازی روی سرور (DevOps)

1. **DNS**: یک رکورد wildcard `*.hamyarfarsh.ir` (یا رکورد جداگانه برای هر زبان) به IP همان VPS.
2. **Nginx**: `server_name` را به `hamyarfarsh.ir *.hamyarfarsh.ir` گسترش دهید؛ همه به همان WSGI/Gunicorn پاس داده شوند.
3. **SSL**: گواهی wildcard برای `*.hamyarfarsh.ir` (Let's Encrypt با DNS-challenge).
4. **متغیر محیطی**: در `.env` مقدار `ALLOWED_HOSTS` را به `.hamyarfarsh.ir,localhost,127.0.0.1` تغییر دهید (نقطهٔ ابتدای دامنه = همهٔ ساب‌دامین‌ها).

---

## فاز ۲ — ترجمهٔ رابط کاربری (در حال انجام)

### ✅ نمونهٔ اول انجام شد (navbar + footer)
- `templates/includes/navbar.html` و `templates/includes/footer.html` با `{% trans %}` / `{% blocktrans %}` تگ‌گذاری شدند.
- فایل‌های ترجمه برای هر ۸ زبان ساخته شد: `locale/<lang>/LC_MESSAGES/django.po`
  (شامل: خانه، ورود، ثبت‌نام، پروفایل، خروج، مدیریت، دسترسی سریع، ارتباط با ما، کپی‌رایت و...).

### برای دیدن نتیجه روی سرور (یک‌بار):
```bash
# نصب ابزار gettext (اگر نصب نیست)
sudo apt-get install gettext

# کامپایل فایل‌های ترجمه به .mo
python manage.py compilemessages

# ری‌استارت سرویس
sudo systemctl restart gunicorn   # یا نام سرویس شما
```
سپس `en.hamyarfarsh.ir` (یا هر ساب‌دامین) را باز کنید؛ منو و فوتر ترجمه‌شده نمایش داده می‌شوند.

### ✅ گروه فروشگاه و محصول انجام شد
- تگ‌گذاری: `templates/shop/catalog.html`، `product_detail.html`، `search.html`.
- مجموع **۱۰۱ رشتهٔ یکتا** (navbar + footer + فروشگاه) در هر ۸ زبان ترجمه و در `.po` ثبت شد.
- اعتبارسنجی شد: تگ‌ها سالم، `blocktrans` متوازن، سازگاری متغیرها (`%(d)s` و...) در همهٔ زبان‌ها درست.
- روش کار (pipeline): اسکریپت تگ‌گذاری خودکار متن‌های امن + اصلاح دستی موارد متغیردار با `blocktrans`، سپس تولید `.po`.

### ✅ گروه حساب کاربری + داشبورد کاربران انجام شد
- تگ‌گذاری: `templates/accounts/` (login, register, profile) و `templates/customer_panel/` (dashboard, orders_history, order_detail, addresses_list, address_form, address_delete, profile_edit).
- مجموع msgidها به **۱۹۱ رشتهٔ یکتا** رسید؛ همگی در هر ۸ زبان ترجمه و اعتبارسنجی شدند.

### ✅ بقیهٔ قالب‌های مشتری‌محور انجام شد
- تگ‌گذاری: صفحهٔ اصلی، سبد خرید/تسویه (orders)، پرداخت و اقساط (payments)، بلاگ/صفحات (pages)، علاقه‌مندی/مقایسه (wishlist)، گالری تصاویر و ویدیو (gallery)، اشتراک کاتالوگ (catalog_app)، تیکت پشتیبانی (live_chat)، اعلان‌ها و خبرنامه.
- جمعاً **۵۹۵ رشتهٔ یکتا** در هر ۸ زبان ترجمه و اعتبارسنجی شد (۵۶ قالب تگ‌گذاری‌شده).
- پنل‌های مدیریتی (dashboard، products، settings، appearance، coupons، home_manager، admin_*) عمداً فارسی نگه داشته شدند.

### چک‌لیست نهایی روی سرور:
```bash
sudo apt-get install gettext      # اگر نصب نیست
python manage.py compilemessages  # ساخت .mo از همهٔ .poها
sudo systemctl restart gunicorn   # یا نام سرویس شما
```

### ادامهٔ فاز ۲ (در صورت نیاز در آینده):
1. تگ‌گذاری بقیهٔ ~۱۲۳ قالب با `{% trans %}` / `{% blocktrans %}` و رشته‌های پایتون با `gettext`.
2. به‌روزرسانی خودکار فایل‌های ترجمه:
   `python manage.py makemessages -l ar -l ur -l en -l ru -l es -l fr -l de -l hi`
   (این دستور msgidهای جدید را به `.po`ها اضافه می‌کند؛ ترجمه‌های موجود حفظ می‌شوند.)
3. پر کردن ترجمه‌های جدید (ماشینی) و سپس `compilemessages`.
4. افزودن CSS حالت LTR برای زبان‌های اروپایی/هندی (سایت فعلاً فقط RTL است).
5. درج سوییچر زبان در هدر: `{% include "includes/language_switcher.html" %}`

> نکته: زبان فارسی فایل `.po` نمی‌خواهد؛ چون msgidها خودِ متن فارسی هستند و به‌صورت پیش‌فرض نمایش داده می‌شوند.

## فاز ۳ — SEO چندزبانه

- تگ‌های `hreflang` برای هر ساب‌دامین، `canonical` صحیح، و sitemap جداگانه per-language.
- داینامیک‌کردن `og:locale` در `base.html`.

## فاز ۴ (اختیاری، در صورت تصمیم بعدی) — ترجمهٔ محتوای دیتابیس

اگر بعداً خواستید نام/توضیح محصولات هم ترجمه شود: نصب `django-modeltranslation`،
ثبت مدل‌ها (Product, Album, Manufacturer, Page و...)، migration و پرکردن محتوا per-language.
