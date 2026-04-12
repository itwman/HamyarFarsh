"""
بازسازی تصاویر شاخص 1000×1000 با نوار اطلاعات رنگی
اجرا: python manage.py rebuild_featured_images
"""
from django.core.management.base import BaseCommand
from products.models import ProductImage
from products.views import generate_thumbnails
from settings_app.models import SiteSettings


class Command(BaseCommand):
    help = 'بازسازی تصاویر شاخص (featured) تمام محصولات با نوار اطلاعات رنگی'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='فقط برای یک محصول خاص بازسازی کن',
        )
        parser.add_argument(
            '--primary-only',
            action='store_true',
            help='فقط تصاویر شاخص (is_primary=True)',
        )

    def handle(self, *args, **options):
        settings = SiteSettings.get_solo()
        
        images = ProductImage.objects.select_related(
            'product__album__manufacturer',
            'product__background_color',
            'product__weave_type',
        ).all()
        
        if options.get('product_id'):
            images = images.filter(product_id=options['product_id'])
        
        if options.get('primary_only'):
            images = images.filter(is_primary=True)
        
        total = images.count()
        self.stdout.write(f'بازسازی {total} تصویر شاخص...')
        
        success = 0
        errors = 0
        
        for i, img in enumerate(images, 1):
            try:
                if img.original and img.original.path:
                    import os
                    if os.path.isfile(img.original.path):
                        generate_thumbnails(img, settings)
                        success += 1
                        self.stdout.write(f'  [{i}/{total}] ✓ {img.product.name}')
                    else:
                        errors += 1
                        self.stdout.write(f'  [{i}/{total}] ✗ فایل یافت نشد: {img.original.path}')
                else:
                    errors += 1
                    self.stdout.write(f'  [{i}/{total}] ✗ بدون فایل اصلی')
            except Exception as e:
                errors += 1
                self.stdout.write(f'  [{i}/{total}] ✗ خطا: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nتکمیل! {success} موفق، {errors} خطا از {total} تصویر.'
        ))
