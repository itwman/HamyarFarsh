"""
Signals برای پردازش خودکار تصاویر و ویدیو
"""
import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductImage, ProductVideo

logger = logging.getLogger(__name__)


# ===== Signal تصاویر =====

@receiver(post_save, sender=ProductImage)
def auto_process_image(sender, instance, created, **kwargs):
    """
    پردازش خودکار تصویر بعد از آپلود:
    - فشرده‌سازی تصویر اصلی (حداکثر 1MB)
    - تولید تامبنیل
    - تولید تصویر شاخص 1000×1000 (فقط برای is_primary)
    """
    from .image_processing import _processing

    # جلوگیری از حلقه بی‌نهایت (process_product_image خودش save میزنه)
    if _processing:
        return

    if not instance.original:
        return

    # فقط وقتی تصویر جدیده یا تامبنیل نداره
    needs_processing = created or not instance.thumbnail

    if needs_processing:
        logger.info(f"Auto-processing image {instance.pk} for product {instance.product_id}")

        def process_in_background():
            from .image_processing import process_product_image
            try:
                process_product_image(instance)
                logger.info(f"Image {instance.pk} processed successfully")
            except Exception as e:
                logger.error(f"Image processing failed for {instance.pk}: {e}")

        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()


# ===== Signal ویدیو =====

@receiver(post_save, sender=ProductVideo)
def auto_process_video(sender, instance, created, **kwargs):
    """
    پردازش خودکار ویدیو بعد از آپلود
    فقط برای ویدیوهای جدید و در صورتی که در وضعیت pending باشند
    """
    if created and instance.original_file and instance.processing_status == 'pending':
        logger.info(f"Triggering automatic processing for video: {instance.id}")

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
