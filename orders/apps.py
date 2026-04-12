"""
پیکربندی اپلیکیشن سفارشات
"""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'سفارشات و سبد خرید'

    def ready(self):
        """Import signals when app is ready"""
        import orders.signals
