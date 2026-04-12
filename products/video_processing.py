"""
سیستم پردازش و بهینه‌سازی ویدیوهای محصول

قابلیت‌ها:
- بررسی کیفیت و رزولوشن ویدیو
- تبدیل به فرمت بهینه (MP4 H.264)
- کاهش رزولوشن به 720p یا 480p
- فشرده‌سازی برای پخش آنلاین
- کاهش حجم با حفظ کیفیت قابل قبول
"""
import os
import subprocess
import logging
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# پیکربندی پیش‌فرض
DEFAULT_MAX_RESOLUTION = '720'  # 720p یا 480p
DEFAULT_VIDEO_CODEC = 'libx264'
DEFAULT_AUDIO_CODEC = 'aac'
DEFAULT_CRF = 23  # Constant Rate Factor (18-28 توصیه می‌شه، 23 = متعادل)
DEFAULT_PRESET = 'medium'  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow


class VideoProcessor:
    """کلاس پردازشگر ویدیو با FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.max_resolution = getattr(settings, 'VIDEO_MAX_RESOLUTION', DEFAULT_MAX_RESOLUTION)
        self.video_codec = getattr(settings, 'VIDEO_CODEC', DEFAULT_VIDEO_CODEC)
        self.audio_codec = getattr(settings, 'AUDIO_CODEC', DEFAULT_AUDIO_CODEC)
        self.crf = getattr(settings, 'VIDEO_CRF', DEFAULT_CRF)
        self.preset = getattr(settings, 'VIDEO_PRESET', DEFAULT_PRESET)
    
    def _find_ffmpeg(self):
        """پیدا کردن مسیر FFmpeg"""
        # بررسی تنظیمات Django
        ffmpeg = getattr(settings, 'FFMPEG_PATH', None)
        if ffmpeg and os.path.isfile(ffmpeg):
            return ffmpeg
        
        # جستجو در PATH سیستم
        try:
            result = subprocess.run(
                ['where', 'ffmpeg'] if os.name == 'nt' else ['which', 'ffmpeg'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception as e:
            logger.warning(f"Could not find ffmpeg in PATH: {e}")
        
        # مسیرهای رایج در Windows
        if os.name == 'nt':
            common_paths = [
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\tools\ffmpeg\bin\ffmpeg.exe',
            ]
            for path in common_paths:
                if os.path.isfile(path):
                    return path
        
        logger.error("FFmpeg not found! Please install FFmpeg.")
        return None
    
    def get_video_info(self, video_path):
        """
        دریافت اطلاعات ویدیو (رزولوشن، مدت زمان، حجم، کدک)
        
        Returns:
            dict: {'width', 'height', 'duration', 'size_mb', 'codec', 'bitrate'}
        """
        if not self.ffmpeg_path:
            logger.error("FFmpeg not available")
            return None
        
        try:
            cmd = [
                self.ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe') if os.name == 'nt' else self.ffmpeg_path.replace('ffmpeg', 'ffprobe'),
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,codec_name,bit_rate,duration',
                '-show_entries', 'format=duration,size',
                '-of', 'default=noprint_wrappers=1',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ffprobe error: {result.stderr}")
                return None
            
            # پارس کردن خروجی
            info = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
            
            # محاسبه حجم فایل
            file_size = os.path.getsize(video_path)
            
            return {
                'width': int(info.get('width', 0)),
                'height': int(info.get('height', 0)),
                'duration': float(info.get('duration', 0)),
                'size_mb': file_size / (1024 * 1024),
                'codec': info.get('codec_name', 'unknown'),
                'bitrate': int(info.get('bit_rate', 0)) if info.get('bit_rate') else None,
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def optimize_video(self, input_path, output_path=None, target_resolution=None):
        """
        بهینه‌سازی ویدیو برای پخش آنلاین
        
        Args:
            input_path: مسیر ویدیو ورودی
            output_path: مسیر ویدیو خروجی (اختیاری)
            target_resolution: رزولوشن هدف (720 یا 480، اختیاری)
        
        Returns:
            str: مسیر فایل بهینه‌شده یا None در صورت خطا
        """
        if not self.ffmpeg_path:
            logger.error("FFmpeg not available - cannot optimize video")
            return None
        
        # بررسی اطلاعات ویدیو
        video_info = self.get_video_info(input_path)
        if not video_info:
            logger.error("Cannot get video info")
            return None
        
        # تعیین رزولوشن هدف
        if target_resolution is None:
            target_resolution = self.max_resolution
        
        target_height = int(target_resolution)
        
        # اگر ویدیو از قبل کوچکتر از هدف است، نیازی به تغییر رزولوشن نیست
        if video_info['height'] <= target_height:
            logger.info(f"Video resolution {video_info['height']}p is already below target {target_height}p")
            target_height = -1  # حفظ رزولوشن اصلی
        
        # تعیین مسیر خروجی
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_optimized{input_file.suffix}")
        
        try:
            # ساخت دستور FFmpeg
            cmd = [
                self.ffmpeg_path,
                '-i', str(input_path),
                '-c:v', self.video_codec,  # کدک ویدیو (H.264)
                '-crf', str(self.crf),  # کیفیت (18-28)
                '-preset', self.preset,  # سرعت/کیفیت encoding
                '-c:a', self.audio_codec,  # کدک صدا (AAC)
                '-b:a', '128k',  # بیت‌ریت صدا
                '-movflags', '+faststart',  # بهینه برای استریم
                '-y',  # بازنویسی فایل خروجی
            ]
            
            # افزودن فیلتر رزولوشن
            if target_height > 0:
                cmd.extend(['-vf', f'scale=-2:{target_height}'])
            
            cmd.append(str(output_path))
            
            logger.info(f"Starting video optimization: {input_path} -> {output_path}")
            logger.info(f"Resolution: {video_info['height']}p -> {target_height if target_height > 0 else video_info['height']}p")
            
            # اجرای FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # حداکثر 10 دقیقه
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
            
            # بررسی نتیجه
            if os.path.exists(output_path):
                optimized_info = self.get_video_info(output_path)
                if optimized_info:
                    logger.info(
                        f"Video optimized successfully: "
                        f"{video_info['size_mb']:.2f}MB -> {optimized_info['size_mb']:.2f}MB "
                        f"({video_info['height']}p -> {optimized_info['height']}p)"
                    )
                return output_path
            else:
                logger.error("Output file not created")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Video optimization timeout (>10 minutes)")
            return None
        except Exception as e:
            logger.error(f"Error optimizing video: {e}")
            return None
    
    def generate_thumbnail(self, video_path, output_path=None, time_offset=1.0):
        """
        ساخت thumbnail از ویدیو
        
        Args:
            video_path: مسیر ویدیو
            output_path: مسیر تصویر خروجی
            time_offset: زمان استخراج فریم (ثانیه)
        
        Returns:
            str: مسیر فایل thumbnail
        """
        if not self.ffmpeg_path:
            return None
        
        if output_path is None:
            video_file = Path(video_path)
            output_path = str(video_file.parent / f"{video_file.stem}_thumb.jpg")
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),
                '-ss', str(time_offset),
                '-vframes', '1',
                '-vf', 'scale=640:-1',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Thumbnail generated: {output_path}")
                return output_path
            else:
                logger.error(f"Thumbnail generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None


# ============================================================
# توابع کمکی برای استفاده در سیگنال‌ها
# ============================================================

def process_product_video(product_video_obj):
    """
    پردازش ویدیوی محصول: بهینه‌سازی + ذخیره
    
    این تابع در سیگنال post_save فراخوانی می‌شود
    """
    if not product_video_obj.video_file:
        return
    
    processor = VideoProcessor()
    
    if not processor.ffmpeg_path:
        logger.warning("FFmpeg not installed - skipping video optimization")
        logger.warning("To enable video optimization, install FFmpeg from https://ffmpeg.org/")
        return
    
    try:
        original_path = product_video_obj.video_file.path
        
        # بررسی اطلاعات ویدیو
        video_info = processor.get_video_info(original_path)
        if not video_info:
            logger.error("Cannot process video - invalid file")
            return
        
        logger.info(
            f"Video info: {video_info['width']}x{video_info['height']}, "
            f"{video_info['size_mb']:.2f}MB, "
            f"codec: {video_info['codec']}"
        )
        
        # بررسی نیاز به بهینه‌سازی
        needs_optimization = (
            video_info['height'] > int(processor.max_resolution) or  # رزولوشن بالا
            video_info['codec'] not in ['h264', 'avc'] or  # کدک غیربهینه
            video_info['size_mb'] > 50  # حجم بالا
        )
        
        if not needs_optimization:
            logger.info("Video already optimized, skipping")
            return
        
        # بهینه‌سازی ویدیو
        video_dir = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        optimized_filename = f"{name}_optimized.mp4"
        optimized_path = os.path.join(video_dir, optimized_filename)
        
        result = processor.optimize_video(
            original_path,
            optimized_path,
            target_resolution=processor.max_resolution
        )
        
        if result and os.path.exists(result):
            # جایگزینی فایل اصلی با نسخه بهینه
            os.remove(original_path)
            os.rename(result, original_path)
            logger.info(f"Video optimized and saved: {original_path}")
        else:
            logger.error("Video optimization failed")
            
    except Exception as e:
        logger.error(f"Error in process_product_video: {e}")


def check_ffmpeg_installation():
    """بررسی نصب بودن FFmpeg"""
    processor = VideoProcessor()
    if processor.ffmpeg_path:
        logger.info(f"FFmpeg found at: {processor.ffmpeg_path}")
        return True
    else:
        logger.warning("FFmpeg not found. Video optimization will be disabled.")
        logger.warning("To install FFmpeg:")
        logger.warning("  Windows: Download from https://ffmpeg.org/download.html")
        logger.warning("  Linux: sudo apt-get install ffmpeg")
        logger.warning("  macOS: brew install ffmpeg")
        return False
