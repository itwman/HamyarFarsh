"""
پردازشگر خودکار ویدیو - بهینه‌سازی برای پخش آنلاین
"""
import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from django.core.files import File
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    logger.warning("ffmpeg-python not installed. Video processing will be disabled.")
    FFMPEG_AVAILABLE = False


def _detect_ffmpeg_path():
    """
    تشخیص خودکار مسیر ffmpeg بر اساس سیستم‌عامل:
    1. اول از settings.FFMPEG_PATH چک می‌کنه
    2. اگر نبود، در PATH دنبال ffmpeg می‌گرده (لینوکس: /usr/bin/ffmpeg)
    3. اگر باز نبود، روی ویندوز مسیرهای رایج رو چک می‌کنه
    """
    # 1. از settings
    custom_path = getattr(settings, 'FFMPEG_PATH', None)
    if custom_path and os.path.isfile(custom_path):
        return custom_path

    # 2. جستجو در PATH (لینوکس/مک پیدا می‌شه)
    found = shutil.which('ffmpeg')
    if found:
        return found

    # 3. مسیرهای رایج ویندوز
    if sys.platform.startswith('win'):
        windows_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\tools\ffmpeg\bin\ffmpeg.exe',
        ]
        for p in windows_paths:
            if os.path.isfile(p):
                return p

    # 4. پیدا نشد
    return None


def _get_ffprobe_path(ffmpeg_path):
    """استخراج مسیر ffprobe از روی مسیر ffmpeg"""
    if not ffmpeg_path:
        return None
    # ویندوز
    if ffmpeg_path.lower().endswith('ffmpeg.exe'):
        return ffmpeg_path[:-10] + 'ffprobe.exe'
    # لینوکس/مک: راه اول = which
    found = shutil.which('ffprobe')
    if found:
        return found
    # جایگزینی اسم
    if ffmpeg_path.endswith('ffmpeg'):
        return ffmpeg_path[:-6] + 'ffprobe'
    return ffmpeg_path.replace('ffmpeg', 'ffprobe')


class VideoProcessor:
    """کلاس بهینه‌سازی ویدیو"""

    # مسیر FFmpeg - تشخیص خودکار در زمان بارگذاری
    FFMPEG_PATH = _detect_ffmpeg_path()
    FFPROBE_PATH = _get_ffprobe_path(FFMPEG_PATH)

    def __init__(self, video_instance):
        """
        Args:
            video_instance: نمونه ProductVideo
        """
        self.video = video_instance
        self.original_path = video_instance.original_file.path
        
    def process(self):
        """پردازش کامل ویدیو"""
        if not FFMPEG_AVAILABLE:
            logger.error("FFmpeg not available for video processing")
            self.video.processing_status = 'failed'
            self.video.processing_error = 'FFmpeg not installed'
            self.video.save()
            return False

        if not self.FFMPEG_PATH:
            err = 'FFmpeg binary not found. Install ffmpeg or set FFMPEG_PATH in settings.'
            logger.error(err)
            self.video.processing_status = 'failed'
            self.video.processing_error = err
            self.video.save()
            return False
        
        try:
            logger.info(f"Starting video processing for: {self.video.id}")
            
            self.video.processing_status = 'processing'
            self.video.processing_progress = 0
            self.video.save()
            
            # 1. استخراج اطلاعات
            self.extract_metadata()
            self.video.processing_progress = 20
            self.video.save()
            
            # 2. ساخت thumbnail
            self.generate_thumbnail()
            self.video.processing_progress = 40
            self.video.save()
            
            # 3. تبدیل به 720p
            if self.video.original_height and self.video.original_height > 720:
                self.convert_to_720p()
                self.video.processing_progress = 70
                self.video.save()
            else:
                logger.info("Video is smaller than 720p, skipping 720p conversion")
            
            # 4. تبدیل به 480p
            self.convert_to_480p()
            self.video.processing_progress = 90
            self.video.save()
            
            # تکمیل موفق
            self.video.processing_status = 'completed'
            self.video.processing_progress = 100
            self.video.processed_at = timezone.now()
            self.video.save()
            
            logger.info(f"Video processing completed successfully: {self.video.id}")
            return True
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}", exc_info=True)
            self.video.processing_status = 'failed'
            self.video.processing_error = str(e)
            self.video.save()
            return False
    
    def extract_metadata(self):
        """استخراج اطلاعات ویدیو"""
        try:
            # استفاده از مسیر ffprobe تشخیص‌داده‌شده
            probe = ffmpeg.probe(self.original_path, cmd=self.FFPROBE_PATH or 'ffprobe')
            
            # پیدا کردن stream ویدیو
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if video_stream:
                self.video.original_width = int(video_stream.get('width', 0))
                self.video.original_height = int(video_stream.get('height', 0))
            
            # مدت زمان
            if 'duration' in probe['format']:
                self.video.duration = float(probe['format']['duration'])
            
            # حجم فایل
            self.video.original_size = os.path.getsize(self.original_path)
            
            self.video.save()
            logger.info(f"Metadata extracted: {self.video.original_width}x{self.video.original_height}")
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            raise
    
    def generate_thumbnail(self):
        """ساخت تصویر پیش‌نمایش از ثانیه اول"""
        try:
            # مسیر فایل thumbnail
            thumb_filename = f"thumb_{self.video.id}.jpg"
            thumb_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', 'thumbnails',
                thumb_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            
            # استخراج فریم
            (
                ffmpeg
                .input(self.original_path, ss=1)
                .filter('scale', 640, -1)
                .output(thumb_path, vframes=1, format='image2')
                .overwrite_output()
                .run(cmd=self.FFMPEG_PATH or 'ffmpeg', capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
            self.video.thumbnail = relative_path
            self.video.save()
            
            logger.info(f"Thumbnail generated: {thumb_filename}")
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            # Thumbnail اجباری نیست، ادامه می‌دهیم
    
    def convert_to_720p(self):
        """تبدیل به 720p با بهینه‌سازی"""
        try:
            output_filename = f"video_{self.video.id}_720p.mp4"
            output_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', '720p',
                output_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"Converting to 720p: {output_filename}")
            
            # تبدیل با FFmpeg
            (
                ffmpeg
                .input(self.original_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    video_bitrate='2M',
                    acodec='aac',
                    audio_bitrate='128k',
                    vf='scale=-2:720',
                    preset='medium',
                    crf=23,
                    **{'profile:v': 'high', 'level': '4.0'}
                )
                .overwrite_output()
                .run(cmd=self.FFMPEG_PATH or 'ffmpeg', capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            self.video.video_720p = relative_path
            self.video.size_720p = os.path.getsize(output_path)
            self.video.save()
            
            logger.info(f"720p conversion completed: {output_filename}")
            
        except Exception as e:
            logger.error(f"720p conversion failed: {str(e)}")
            raise
    
    def convert_to_480p(self):
        """تبدیل به 480p - بهینه برای موبایل"""
        try:
            output_filename = f"video_{self.video.id}_480p.mp4"
            output_path = os.path.join(
                settings.MEDIA_ROOT,
                'products', 'videos', '480p',
                output_filename
            )
            
            # ایجاد فولدر
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"Converting to 480p: {output_filename}")
            
            # تبدیل با FFmpeg
            (
                ffmpeg
                .input(self.original_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    video_bitrate='1M',
                    acodec='aac',
                    audio_bitrate='96k',
                    vf='scale=-2:480',
                    preset='medium',
                    crf=23,
                    **{'profile:v': 'main', 'level': '3.1'}
                )
                .overwrite_output()
                .run(cmd=self.FFMPEG_PATH or 'ffmpeg', capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # ذخیره در مدل
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            self.video.video_480p = relative_path
            self.video.size_480p = os.path.getsize(output_path)
            self.video.save()
            
            logger.info(f"480p conversion completed: {output_filename}")
            
        except Exception as e:
            logger.error(f"480p conversion failed: {str(e)}")
            raise


def process_video(video_id):
    """
    تابع کمکی برای پردازش ویدیو
    
    Args:
        video_id: ID ویدیو
        
    Returns:
        bool: موفق/ناموفق
    """
    from products.models import ProductVideo
    
    try:
        video = ProductVideo.objects.get(id=video_id)
        processor = VideoProcessor(video)
        return processor.process()
    except ProductVideo.DoesNotExist:
        logger.error(f"Video {video_id} not found")
        return False
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        return False
