# 🚀 راهنمای نصب فاز 8 - سیستم پرداخت و مالی

## ✅ مراحل نصب و راه‌اندازی

### 1️⃣ نصب کتابخانه‌های جدید

```bash
cd C:\xampp\htdocs\Hamyarfarsh
venv\Scripts\activate
pip install requests python-dateutil
```

### 2️⃣ اجرای Migration

```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 3️⃣ راه‌اندازی سرور

```bash
python manage.py runserver 0.0.0.0:8200
```

### 4️⃣ تنظیمات در Django Admin

1. وارد پنل ادمین شوید: http://localhost:8200/admin/
2. به بخش **Payment Gateways** بروید
3. یک درگاه زرین‌پال جدید بسازید:
   - **نام درگاه**: zarinpal
   - **Merchant ID**: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX (از زرین‌پال دریافت کنید)
   - **فعال**: ✅
   - **حالت تست**: ✅ (برای تست)

4. به بخش **Site Settings** بروید و بررسی کنید:
   - نرخ سود چک ماهانه: 2.5%
   - نرخ سود چک دوماهانه: 2.7%
   - نرخ سود بتا: 2.5%
   - سقف اقساط: 75,000,000 تومان
   - حداکثر ماه‌های چک: 12
   - حداکثر ماه‌های بتا: 18

---

## 🎯 URL های موجود

```
http://localhost:8200/payments/calculator/        - محاسبه‌گر اقساط
http://localhost:8200/payments/invoice/1/         - فاکتور سفارش 1
http://localhost:8200/payments/request/1/         - درخواست پرداخت سفارش 1
```

---

## 🧪 تست فرآیند پرداخت

### مرحله 1: ایجاد یک سفارش تستی
1. وارد سایت شوید
2. محصولی را به سبد اضافه کنید
3. فرآیند ثبت سفارش را کامل کنید

### مرحله 2: تست پرداخت
1. روی دکمه "پرداخت" کلیک کنید
2. به درگاه زرین‌پال هدایت می‌شوید
3. در حالت Sandbox از کارت‌های تستی استفاده کنید:
   - شماره کارت: 6274-1211-0000-0000
   - CVV2: هر عددی
   - تاریخ: هر تاریخی در آینده
   - رمز دوم: 123456

### مرحله 3: بررسی نتیجه
- پرداخت موفق: صفحه success با کد پیگیری
- پرداخت ناموفق: صفحه failed با پیام خطا

---

## 📊 تست محاسبه‌گر اقساط

1. به آدرس `/payments/calculator/` بروید
2. اطلاعات زیر را وارد کنید:
   - مبلغ کل: 50,000,000 تومان
   - پیش‌پرداخت: 20,000,000 تومان  
   - نوع طرح: چک صیادی
   - تعداد اقساط: 12
   - دوره: ماهانه

3. نتیجه باید باشد:
   - مانده: 30,000,000
   - سود: 9,000,000 (30M × 2.5% × 12)
   - مبلغ کل: 39,000,000
   - هر قسط: 3,250,000 تومان

---

## 🎨 ویژگی‌های پیاده‌سازی شده

### فاز 8.1: پرداخت آنلاین ✅
- ✅ اتصال به زرین‌پال
- ✅ پرداخت کامل نقدی
- ✅ پرداخت بیعانه
- ✅ Callback و Verify
- ✅ لاگ تراکنش‌ها
- ✅ ذخیره IP و User Agent

### فاز 8.2: سیستم اقساطی ✅
- ✅ طرح چکی (12 ماه)
- ✅ طرح بتا (18 ماه)
- ✅ محاسبه‌گر اقساط
- ✅ پرداخت ماهانه/دوماهانه
- ✅ محاسبه سود
- ✅ جدول اقساط
- ✅ ثبت اطلاعات چک

### فاز 8.3: فاکتور و قیمت روز ✅
- ✅ فاکتور حرفه‌ای
- ✅ جدول اقلام
- ✅ اطلاعات پرداخت
- ✅ جزئیات اقساط
- ✅ قابلیت چاپ
- ✅ شرایط فروش

---

## 🔍 بررسی نصب صحیح

### چک کردن مدل‌ها در Admin
```bash
python manage.py shell
```

```python
from payments.models import PaymentGateway, Transaction, InstallmentPlan

# تعداد درگاه‌ها
print(f"Gateways: {PaymentGateway.objects.count()}")

# تعداد تراکنش‌ها
print(f"Transactions: {Transaction.objects.count()}")

# تعداد طرح‌های اقساط
print(f"Installment Plans: {InstallmentPlan.objects.count()}")
```

### چک کردن URL ها
```bash
python manage.py show_urls | grep payments
```

باید نتایج زیر رو ببینید:
```
/payments/request/<int:order_id>/
/payments/callback/
/payments/verify/<str:tracking_code>/
/payments/success/<str:tracking_code>/
/payments/failed/<str:tracking_code>/
/payments/calculator/
/payments/calculator/api/
/payments/invoice/<int:order_id>/
```

---

## ⚠️ مشکلات رایج و راه‌حل

### 1. خطا: "No module named 'requests'"
```bash
pip install requests
```

### 2. خطا: "No module named 'dateutil'"
```bash
pip install python-dateutil
```

### 3. خطا: "No such table: payment_gateways"
```bash
python manage.py migrate payments
```

### 4. درگاه پرداخت کار نمی‌کند
- Merchant ID را از زرین‌پال دریافت کنید
- حالت Sandbox را فعال کنید
- URL callback باید از اینترنت قابل دسترسی باشد

### 5. محاسبه‌گر اقساط عدد اشتباه نشان می‌دهد
- تنظیمات SiteSettings را چک کنید
- نرخ سود را بررسی کنید
- فرمول: مانده × (نرخ ÷ 100) × تعداد ماه

---

## 📝 کامندهای مفید

### ایجاد اقساط برای طرح تأیید شده
```bash
python manage.py create_installments
```

### ایجاد اقساط برای یک طرح خاص
```bash
python manage.py create_installments --plan-id=1
```

---

## 🔐 تنظیمات امنیتی Production

1. **DEBUG = False** در production
2. **HTTPS** برای درگاه پرداخت
3. **Merchant ID** را در .env ذخیره کنید
4. **Sandbox = False** در production
5. **ALLOWED_HOSTS** را محدود کنید

---

## 📞 دریافت Merchant ID از زرین‌پال

1. به https://zarinpal.com بروید
2. ثبت‌نام یا ورود کنید
3. پنل پذیرنده → درگاه پرداخت
4. Merchant ID خود را کپی کنید

برای تست: از حالت Sandbox استفاده کنید

---

✅ **فاز 8 با موفقیت نصب شد!**

اگر مشکلی بود، لاگ خطاها رو چک کنید:
```bash
python manage.py runserver 0.0.0.0:8200
```
