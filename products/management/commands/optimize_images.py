"""بهینه‌سازی هوشمند تصاویر محصولات"""
from django.core.management.base import BaseCommand
from products.models import ProductImage
from products.image_processing import process_product_image


class Command(BaseCommand):
    help = 'بهینه‌سازی تصاویر - فقط تصاویری که نیاز دارن'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='همه تصاویر')
        parser.add_argument('--max-size', type=float, default=1.0, help='حداکثر MB')
        parser.add_argument('--product', type=int, help='فقط یک محصول')
        parser.add_argument('--dry-run', action='store_true', help='فقط گزارش')

    def handle(self, *args, **options):
        qs = ProductImage.objects.select_related(
            'product', 'product__album',
            'product__album__manufacturer',
            'product__background_color')
        if options['product']:
            qs = qs.filter(product_id=options['product'])
        max_bytes = int(options['max_size'] * 1024 * 1024)
        needs = []
        for img in qs:
            reasons = []
            if not img.thumbnail:
                reasons.append('no-thumb')
            if img.is_primary and not img.featured_image:
                reasons.append('no-featured')
            if img.original:
                try:
                    if img.original.size > max_bytes:
                        reasons.append('big:%.1fMB' % (img.original.size / 1024 / 1024))
                except Exception:
                    pass
            if options['all'] and not reasons:
                reasons.append('reprocess')
            if reasons:
                needs.append((img, reasons))
        self.stdout.write('Total: %d | Need: %d' % (qs.count(), len(needs)))
        if not needs:
            self.stdout.write(self.style.SUCCESS('All optimized!'))
            return
        if options['dry_run']:
            for img, r in needs:
                self.stdout.write('  [%d] %s - %s' % (img.pk, img.product.name, ','.join(r)))
            return
        ok = err = 0
        for i, (img, r) in enumerate(needs, 1):
            try:
                process_product_image(img)
                self.stdout.write('  [%d/%d] OK %s' % (i, len(needs), img.product.name))
                ok += 1
            except Exception as e:
                self.stderr.write('  [%d/%d] ERR: %s' % (i, len(needs), e))
                err += 1
        self.stdout.write(self.style.SUCCESS('Done: %d ok, %d err' % (ok, err)))
