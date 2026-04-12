@echo off
REM ==========================================
REM اضافه کردن FFmpeg به PATH سیستم
REM ==========================================
echo.
echo اضافه کردن FFmpeg به PATH...
echo.

REM اضافه کردن به PATH (فقط برای session فعلی)
set PATH=%PATH%;C:\ffmpeg\bin
echo [OK] FFmpeg به PATH session فعلی اضافه شد

REM تست
ffmpeg -version
if %errorlevel% equ 0 (
    echo.
    echo [موفق] FFmpeg در دسترس است!
    echo.
) else (
    echo.
    echo [خطا] هنوز FFmpeg در دسترس نیست
    echo.
)

echo ==========================================
echo برای اضافه کردن دائمی به PATH:
echo ==========================================
echo 1. کنترل پنل ^> سیستم ^> تنظیمات پیشرفته سیستم
echo 2. متغیرهای محیطی ^> Path
echo 3. اضافه کردن: C:\ffmpeg\bin
echo ==========================================
echo.

REM یا اضافه کردن خودکار به PATH کاربر
setx PATH "%PATH%;C:\ffmpeg\bin"
if %errorlevel% equ 0 (
    echo [OK] FFmpeg به PATH دائمی کاربر اضافه شد
    echo لطفا Command Prompt را ببندید و دوباره باز کنید
) else (
    echo [هشدار] اضافه کردن خودکار ممکن است نیاز به دسترسی Admin داشته باشد
)

echo.
pause
