"""دستور مدیریتی: پردازش مجدد تمام تصاویر"""
from django.core.management.base import BaseCommand
from products.models import ProductImage
from products.image_processing import process_product_image


class Command(BaseCommand):
    help = 'پردازش مجدد تمام تصاویر محصولات (فشرده‌سازی + تامبنیل + شاخص)'

    def add_arguments(self, parser):
        parser.add_argument('--product', type=int, help='فقط تصاویر یک محصول خاص')
        parser.add_argument('--primary-only', action='store_true', help='فقط تصاویر شاخص')

    def handle(self, *args, **options):
        qs = ProductImage.objects.select_related('product')
        if options['product']:
            qs = qs.filter(product_id=options['product'])
        if options['primary_only']:
            qs = qs.filter(is_primary=True)

        total = qs.count()
        self.stdout.write(f'پردازش {total} تصویر...')

        success = 0
        for i, img in enumerate(qs, 1):
            try:
                process_product_image(img)
                self.stdout.write(f'  [{i}/{total}] {img.product.name} - OK')
                success += 1
            except Exception as e:
                self.stderr.write(f'  [{i}/{total}] {img.product.name} - ERROR: {e}')

        self.stdout.write(self.style.SUCCESS(f'پردازش تمام شد: {success}/{total} موفق'))
