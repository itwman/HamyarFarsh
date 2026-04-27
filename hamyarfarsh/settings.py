"""
تنظیمات Django - پروژه همیار فرش (HamyarFarsh)
Django 5 + MySQL + Bootstrap 5 RTL + Vazirmatn
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ============================================================
# MariaDB 10.4 compatibility patch for Django 5
# ============================================================
import django.db.backends.mysql.features as mysql_features
import django.db.backends.base.base as base_backend

# Patch 1: Skip version check
_original_check = base_backend.BaseDatabaseWrapper.check_database_version_supported
def _patched_check(self):
    try:
        _original_check(self)
    except Exception:
        pass
base_backend.BaseDatabaseWrapper.check_database_version_supported = _patched_check

# Patch 2: Minimum version
if hasattr(mysql_features.DatabaseFeatures, 'minimum_database_version'):
    mysql_features.DatabaseFeatures.minimum_database_version = (10, 4)

# Patch 3: Disable RETURNING clause (MariaDB 10.4 doesn't support it)
mysql_features.DatabaseFeatures.can_return_columns_from_insert = False
mysql_features.DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
# ============================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF trusted origins (Django 4+)
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8300',
    'http://localhost:8300',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://hamyarfarsh.ir',
    'https://www.hamyarfarsh.ir',
]

# Ensure CSRF cookie is accessible
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Apps
    'accounts.apps.AccountsConfig',
    'settings_app.apps.SettingsAppConfig',
    'catalog.apps.CatalogConfig',
    'products.apps.ProductsConfig',
    'shop.apps.ShopConfig',
    'orders.apps.OrdersConfig',  # فاز 7
    'payments.apps.PaymentsConfig',  # فاز 8
    'dashboard',
    'catalog_app',
    'api',
    'customer_panel',
    'gallery.apps.GalleryConfig',
    'pages.apps.PagesConfig',
    'home_manager.apps.HomeManagerConfig',
    'appearance.apps.AppearanceConfig',
    'coupons.apps.CouponsConfig',
    'wishlist.apps.WishlistConfig',
    'notifications.apps.NotificationsConfig',
    'newsletter.apps.NewsletterConfig',
    'live_chat.apps.LiveChatConfig',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hamyarfarsh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'settings_app.context_processors.site_settings',
                'pages.context_processors.cms_pages',
                'appearance.context_processors.appearance_context',
                'wishlist.context_processors.wishlist_compare_context',
                'notifications.context_processors.notifications_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'hamyarfarsh.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'hamyarfarsh_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================
# تنظیمات تصاویر
# ============================================================
THUMBNAIL_SIZE = (350, 350)
FEATURED_IMAGE_SIZE = (1000, 1000)
MAX_IMAGE_SIZE_MB = 1

# ============================================================
# تنظیمات پردازش ویدیو
# ============================================================
# مسیر FFmpeg (اختیاری - اگر در PATH نباشد)
# FFMPEG_PATH = r'C:\ffmpeg\bin\ffmpeg.exe'

# حداکثر رزولوشن ویدیو (720 یا 480)
VIDEO_MAX_RESOLUTION = '720'

# کدک ویدیو (H.264 برای سازگاری بالا)
VIDEO_CODEC = 'libx264'

# کدک صدا
AUDIO_CODEC = 'aac'

# CRF - Constant Rate Factor (18-28)
# کمتر = کیفیت بالاتر + حجم بیشتر
# بیشتر = کیفیت پایین‌تر + حجم کمتر
# توصیه: 23 (متعادل)
VIDEO_CRF = 23

# Preset کدگذاری (سرعت/کیفیت)
# ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# توصیه: medium (متعادل)
VIDEO_PRESET = 'medium'

# حداکثر حجم فایل ویدیو قبل از آپلود (مگابایت)
MAX_VIDEO_SIZE_MB = 100

# ============================================================
# تنظیمات سبد خرید (فاز 7)
# ============================================================
CART_SESSION_ID = 'cart'
