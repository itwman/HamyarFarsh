"""
Signals برای پردازش خودکار ویدیو
"""
import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVideo

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ProductVideo)
def auto_process_video(sender, instance, created, **kwargs):
    """
    پردازش خودکار ویدیو بعد از آپلود
    
    فقط برای ویدیوهای جدید و در صورتی که در وضعیت pending باشند
    """
    if created and instance.original_file and instance.processing_status == 'pending':
        logger.info(f"Triggering automatic processing for video: {instance.id}")
        
        # پردازش در thread جداگانه تا request block نشه
        def process_in_background():
            from utils.video_processor import process_video
            try:
                process_video(instance.id)
            except Exception as e:
                logger.error(f"Background video processing failed: {str(e)}")
        
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Background processing started for video: {instance.id}")
