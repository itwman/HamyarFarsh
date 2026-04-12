"""ایجاد بخش‌های پیش‌فرض صفحه اصلی"""
from django.db import migrations


def create_defaults(apps, schema_editor):
    HomeSection = apps.get_model('home_manager', 'HomeSection')

    defaults = [
        {
            'title': 'جدیدترین محصولات',
            'icon': 'bi-lightning',
            'section_type': 'product_auto',
            'auto_filter': 'newest',
            'item_count': 8,
            'order': 1,
            'show_more_link': '/farsh/',
        },
        {
            'title': 'محصولات ویژه',
            'icon': 'bi-star-fill',
            'section_type': 'product_auto',
            'auto_filter': 'featured',
            'item_count': 8,
            'order': 2,
            'show_more_link': '/farsh/',
        },
        {
            'title': 'پربازدیدترین محصولات',
            'icon': 'bi-fire',
            'section_type': 'product_auto',
            'auto_filter': 'popular',
            'item_count': 8,
            'order': 3,
            'bg_color': '#F5F5F5',
            'show_more_link': '/farsh/',
        },
        {
            'title': 'برندهای همکار',
            'icon': 'bi-building',
            'section_type': 'brands',
            'item_count': 12,
            'order': 4,
        },
    ]

    for data in defaults:
        if not HomeSection.objects.filter(title=data['title']).exists():
            HomeSection.objects.create(**data)
            print(f"  -> بخش '{data['title']}' ایجاد شد")


class Migration(migrations.Migration):
    dependencies = [
        ('home_manager', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_defaults, migrations.RunPython.noop),
    ]
