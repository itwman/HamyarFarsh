"""
سیگنال‌های اپلیکیشن سفارشات
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderStatusLog


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """ثبت تغییر وضعیت سفارش"""
    if instance.pk:  # سفارش از قبل وجود دارد
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # ثبت لاگ تغییر وضعیت
                OrderStatusLog.objects.create(
                    order=instance,
                    old_status=old_order.status,
                    new_status=instance.status,
                    changed_by=None,  # باید از request گرفته شود
                    notes=f'تغییر وضعیت از {old_order.get_status_display_persian()} به {instance.get_status_display_persian()}'
                )
        except Order.DoesNotExist:
            pass
