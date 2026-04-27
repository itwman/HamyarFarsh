"""تولید SKU برای محصولات قدیمی که SKU ندارن"""
import random
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'تولید SKU خودکار برای محصولاتی که کد ندارن'

    def handle(self, *args, **options):
        products = Product.objects.filter(sku='').select_related('album')
        total = products.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('همه محصولات SKU دارن!'))
            return
        self.stdout.write(f'{total} محصول بدون SKU...')
        existing = set(Product.objects.exclude(sku='').values_list('sku', flat=True))
        count = 0
        for p in products:
            comb = p.album.comb
            while True:
                code = random.randint(10000, 99999)
                sku = f'IR{comb}-{code}'
                if sku not in existing:
                    existing.add(sku)
                    p.sku = sku
                    p.save(update_fields=['sku'])
                    count += 1
                    break
        self.stdout.write(self.style.SUCCESS(f'{count} SKU تولید شد.'))
