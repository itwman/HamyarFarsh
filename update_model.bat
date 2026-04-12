@echo off
REM ==========================================
REM اجرای اسکریپت جایگزینی ProductVideo
REM ==========================================
cd /d C:\xampp\htdocs\Hamyarfarsh

echo.
echo ==========================================
echo جایگزینی خودکار مدل ProductVideo
echo ==========================================
echo.

python update_product_video_model.py

if %errorlevel% equ 0 (
    echo.
    echo آیا می‌خواهید Migration را هم اجرا کنید؟
    set /p RUN_MIGRATION="اجرای Migration؟ (y/n): "
    
    if /i "%RUN_MIGRATION%"=="y" (
        echo.
        echo ساخت Migration...
        python manage.py makemigrations products
        
        echo.
        echo اجرای Migration...
        python manage.py migrate products
        
        echo.
        echo [OK] Migration تکمیل شد!
    )
)

echo.
pause
