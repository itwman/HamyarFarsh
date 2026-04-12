@echo off
REM ==========================================
REM نصب کامل سیستم بهینه‌سازی ویدیو
REM ==========================================
cd /d C:\xampp\htdocs\Hamyarfarsh

echo.
echo ==========================================
echo نصب سیستم بهینه‌سازی ویدیو
echo ==========================================
echo.

echo [1/7] اضافه کردن FFmpeg به PATH...
set PATH=%PATH%;C:\ffmpeg\bin
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [خطا] FFmpeg در دسترس نیست!
    pause
    exit /b 1
)
echo [OK] FFmpeg آماده است
echo.

echo [2/7] نصب کتابخانه‌های Python...
pip install ffmpeg-python Pillow
if %errorlevel% neq 0 (
    echo [خطا] نصب کتابخانه‌ها ناموفق بود
    pause
    exit /b 1
)
echo [OK] کتابخانه‌ها نصب شدند
echo.

echo [3/7] ساخت فولدرهای مورد نیاز...
mkdir media\products\videos\originals 2>nul
mkdir media\products\videos\720p 2>nul
mkdir media\products\videos\480p 2>nul
mkdir media\products\videos\thumbnails 2>nul
echo [OK] فولدرها ساخته شدند
echo.

echo [4/7] بررسی فایل‌های ضروری...
if not exist "utils\video_processor.py" (
    echo [خطا] utils\video_processor.py وجود ندارد!
    pause
    exit /b 1
)
if not exist "products\signals.py" (
    echo [خطا] products\signals.py وجود ندارد!
    pause
    exit /b 1
)
echo [OK] فایل‌ها موجود هستند
echo.

echo [5/7] آیا مدل ProductVideo را آپدیت کردید؟
echo محتوای products\models_productvideo_new.py را باید جایگزین ProductVideo کنید
echo.
set /p UPDATED="آیا این کار را انجام دادید؟ (y/n): "
if /i not "%UPDATED%"=="y" (
    echo.
    echo لطفا ابتدا مدل را آپدیت کنید، سپس دوباره این اسکریپت را اجرا کنید.
    pause
    exit /b 1
)
echo.

echo [6/7] ساخت و اجرای Migration...
python manage.py makemigrations products
if %errorlevel% neq 0 (
    echo [خطا] ساخت migration ناموفق بود
    pause
    exit /b 1
)

python manage.py migrate products
if %errorlevel% neq 0 (
    echo [خطا] اجرای migration ناموفق بود
    pause
    exit /b 1
)
echo [OK] Migration انجام شد
echo.

echo [7/7] تست سیستم...
python -c "from utils.video_processor import VideoProcessor; print('VideoProcessor OK')"
if %errorlevel% neq 0 (
    echo [هشدار] تست VideoProcessor ناموفق بود
) else (
    echo [OK] سیستم آماده است!
)
echo.

echo ==========================================
echo نصب با موفقیت تکمیل شد!
echo ==========================================
echo.
echo مراحل بعدی:
echo 1. سرور را ریستارت کنید: python manage.py runserver 0.0.0.0:8200
echo 2. وارد Admin Panel شوید
echo 3. یک ویدیو آپلود کنید و منتظر پردازش بمانید
echo.
echo راهنمای کامل: docs\VIDEO_IMPLEMENTATION_GUIDE.md
echo.
pause
