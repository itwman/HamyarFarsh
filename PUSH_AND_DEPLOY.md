# ارسال به گیت‌هاب و استقرار روی سرور — چندزبانه‌سازی

## ۱) روی سیستم خودتان (ویندوز) — در پوشهٔ پروژه

ابتدا قفل کهنهٔ گیت را حذف کنید (از محیط ابزار باقی مانده و قابل حذف نبود):

```cmd
del .git\index.lock
del .git\_writetest
```

سپس بررسی، ثبت و ارسال:

```cmd
git status
git add -A
git commit -m "feat(i18n): چندزبانه‌سازی با ساب‌دامین + ترجمهٔ کامل رابط (۸ زبان، ۵۹۵ رشته)"
git push origin main
```

> فایل‌های `venv/`، `.env`، `staticfiles/` در `.gitignore` هستند و ارسال نمی‌شوند. ✅
> فایل‌های `locale/*/LC_MESSAGES/django.po` باید ارسال شوند (هستند). فایل‌های `.mo` روی سرور ساخته می‌شوند.

---

## ۲) روی سرور (VPS) — بعد از push

```bash
cd /path/to/HamyarFarsh          # مسیر پروژه روی سرور
git pull origin main

# نصب ابزار ترجمه (یک‌بار، اگر نصب نیست)
sudo apt-get update && sudo apt-get install -y gettext

# فعال‌سازی محیط مجازی
source venv/bin/activate

# کامپایل فایل‌های ترجمه (.po -> .mo)
python manage.py compilemessages

# اگر استاتیک تغییر کرده
python manage.py collectstatic --noinput

# ری‌استارت سرویس (نام سرویس خود را بگذارید)
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

---

## ۳) DNS و Nginx (برای فعال‌شدن ساب‌دامین‌ها)

- رکورد DNS: `*.hamyarfarsh.ir` → IP سرور (یا رکورد جدا برای هر زبان: en, ar, ru, es, fr, de, ur, hi).
- در بلوک Nginx، `server_name` را گسترش دهید:
  ```nginx
  server_name hamyarfarsh.ir www.hamyarfarsh.ir *.hamyarfarsh.ir;
  ```
- در `.env` سرور:
  ```
  ALLOWED_HOSTS=.hamyarfarsh.ir,localhost,127.0.0.1
  ```
- SSL: گواهی wildcard برای `*.hamyarfarsh.ir` (Let's Encrypt با DNS-challenge).

---

## ۴) تست بعد از استقرار

- `en.hamyarfarsh.ir` → رابط انگلیسی (LTR)
- `ar.hamyarfarsh.ir` → عربی (RTL)
- `hamyarfarsh.ir` → فارسی (پیش‌فرض)

---

## کارهای باقی‌مانده برای آینده (غیر فوری)

1. **مخفی‌سازی روش‌های پرداخت ایرانی در سایت خارجی**: فروش اقساطی، چک صیادی، طرح بتا بانک رفاه فقط برای ایران است. روی ساب‌دامین‌های خارجی باید با یک شرط ساده مخفی شوند (`{% if LANGUAGE_CODE == 'fa' %}`). در جریان خارجی پرداخت آنلاین نداریم؛ فقط استعلام/پیش‌فاکتور.
2. **ارز و قیمت بین‌المللی** (دستی + حاشیه سود، مدل Currency).
3. **نمایش/مخفی قیمت per-language** (پیش‌فرض خاموش برای زبان‌های خارجی).
4. **فرم درخواست پیش‌فاکتور صادراتی** (دریافت شمارهٔ تماس به‌جای پرداخت).
5. **نام نقشهٔ per-language** (آوانگاری لاتین + کد یکتای کوتاه).
6. بازبینی انسانی ترجمه‌های ماشینی در فایل‌های `.po` (اختیاری).
