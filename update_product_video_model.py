#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت خودکار برای جایگزینی کلاس ProductVideo در models.py
"""
import os
import sys
import re
from datetime import datetime

# مسیرها
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_FILE = os.path.join(BASE_DIR, 'products', 'models.py')
NEW_VIDEO_MODEL_FILE = os.path.join(BASE_DIR, 'products', 'models_productvideo_new.py')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# رنگ‌ها برای خروجی (Windows compatible)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def create_backup():
    """ساخت بک‌اپ از models.py"""
    try:
        # ساخت فولدر بک‌اپ
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # نام فایل بک‌اپ با تاریخ
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(BACKUP_DIR, f'models_backup_{timestamp}.py')
        
        # کپی فایل
        with open(MODELS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success(f"بک‌اپ ایجاد شد: {backup_file}")
        return True
    except Exception as e:
        print_error(f"خطا در ایجاد بک‌اپ: {str(e)}")
        return False

def read_new_video_model():
    """خواندن کلاس جدید ProductVideo"""
    try:
        with open(NEW_VIDEO_MODEL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # استخراج کلاس ProductVideo
        # پیدا کردن شروع کلاس
        class_start = content.find('class ProductVideo')
        if class_start == -1:
            print_error("کلاس ProductVideo در فایل جدید یافت نشد!")
            return None
        
        # حذف کامنت‌های اول فایل
        new_model = content[class_start:]
        
        print_success("کلاس جدید ProductVideo خوانده شد")
        return new_model
    except FileNotFoundError:
        print_error(f"فایل {NEW_VIDEO_MODEL_FILE} یافت نشد!")
        return None
    except Exception as e:
        print_error(f"خطا در خواندن فایل جدید: {str(e)}")
        return None

def replace_video_model():
    """جایگزینی کلاس ProductVideo در models.py"""
    try:
        # خواندن فایل models.py
        with open(MODELS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # پیدا کردن شروع و پایان کلاس ProductVideo فعلی
        # الگوی regex برای پیدا کردن کلاس
        pattern = r'class ProductVideo\(models\.Model\):.*?(?=\n(?:class |$))'
        
        # پیدا کردن کلاس
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print_error("کلاس ProductVideo فعلی در models.py یافت نشد!")
            return False
        
        old_class_start = match.start()
        old_class_end = match.end()
        
        print_info(f"کلاس قدیمی یافت شد (خط {content[:old_class_start].count(chr(10)) + 1})")
        
        # خواندن کلاس جدید
        new_class = read_new_video_model()
        if not new_class:
            return False
        
        # جایگزینی
        new_content = (
            content[:old_class_start] +
            new_class +
            '\n\n' +
            content[old_class_end:]
        )
        
        # نوشتن فایل جدید
        with open(MODELS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print_success("کلاس ProductVideo با موفقیت جایگزین شد!")
        return True
        
    except Exception as e:
        print_error(f"خطا در جایگزینی: {str(e)}")
        return False

def verify_changes():
    """بررسی تغییرات انجام شده"""
    try:
        with open(MODELS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # بررسی وجود فیلدهای جدید
        new_fields = [
            'original_file',
            'video_720p',
            'video_480p',
            'thumbnail',
            'duration',
            'processing_status',
            'processing_progress',
        ]
        
        missing_fields = []
        for field in new_fields:
            if field not in content:
                missing_fields.append(field)
        
        if missing_fields:
            print_warning(f"فیلدهای زیر یافت نشدند: {', '.join(missing_fields)}")
            return False
        
        print_success("تمام فیلدهای جدید موجود هستند")
        
        # شمارش تعداد خطوط
        lines = content.split('\n')
        product_video_lines = 0
        in_class = False
        
        for line in lines:
            if 'class ProductVideo' in line:
                in_class = True
            elif in_class and line.startswith('class '):
                break
            elif in_class:
                product_video_lines += 1
        
        print_info(f"کلاس ProductVideo جدید: {product_video_lines} خط")
        
        return True
        
    except Exception as e:
        print_error(f"خطا در بررسی تغییرات: {str(e)}")
        return False

def main():
    """تابع اصلی"""
    print("\n" + "=" * 60)
    print("  اسکریپت جایگزینی خودکار ProductVideo")
    print("=" * 60 + "\n")
    
    # بررسی وجود فایل‌ها
    if not os.path.exists(MODELS_FILE):
        print_error(f"فایل models.py یافت نشد: {MODELS_FILE}")
        return False
    
    if not os.path.exists(NEW_VIDEO_MODEL_FILE):
        print_error(f"فایل ProductVideo جدید یافت نشد: {NEW_VIDEO_MODEL_FILE}")
        return False
    
    print_info(f"فایل models.py: {MODELS_FILE}")
    print_info(f"فایل ProductVideo جدید: {NEW_VIDEO_MODEL_FILE}")
    print()
    
    # تأیید از کاربر
    print_warning("این عملیات کلاس ProductVideo فعلی را جایگزین می‌کند.")
    print_warning("بک‌اپ خودکار ایجاد می‌شود.")
    print()
    
    response = input("آیا مطمئن هستید؟ (y/n): ").lower().strip()
    if response not in ['y', 'yes', 'بله']:
        print_info("عملیات لغو شد.")
        return False
    
    print()
    
    # مراحل اجرا
    steps = [
        ("ایجاد بک‌اپ", create_backup),
        ("جایگزینی کلاس ProductVideo", replace_video_model),
        ("بررسی تغییرات", verify_changes),
    ]
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {step_name}...")
        if not step_func():
            print_error("عملیات با خطا مواجه شد!")
            print_info("می‌توانید از بک‌اپ برای بازگشت استفاده کنید.")
            return False
        print()
    
    print("=" * 60)
    print_success("عملیات با موفقیت تکمیل شد!")
    print("=" * 60)
    print()
    
    print_info("مراحل بعدی:")
    print("  1. اجرای Migration:")
    print("     python manage.py makemigrations products")
    print("     python manage.py migrate products")
    print()
    print("  2. ریستارت سرور:")
    print("     python manage.py runserver 0.0.0.0:8200")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_warning("عملیات توسط کاربر لغو شد.")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"خطای غیرمنتظره: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
