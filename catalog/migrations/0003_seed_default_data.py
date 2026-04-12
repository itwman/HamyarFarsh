"""
Data migration: اضافه کردن سایزهای استاندارد فرش
"""
import math
from django.db import migrations


def add_default_sizes(apps, schema_editor):
    CarpetSize = apps.get_model('catalog', 'CarpetSize')

    sizes = [
        # name, size_type, length, width, diameter, area, is_nine_meter, default_order_rule, sort_order
        ('12 متری', 'rectangular', 4.00, 3.00, None, 12.0000, False, 'any', 1),
        ('9 متری (3.50×2.50)', 'rectangular', 3.50, 2.50, None, 8.7500, True, 'any', 2),
        ('6 متری', 'rectangular', 3.00, 2.00, None, 6.0000, False, 'any', 3),
        ('9 متری مربع', 'rectangular', 3.00, 3.00, None, 9.0000, False, 'even', 4),
        ('15 متری', 'rectangular', 5.00, 3.00, None, 15.0000, False, 'even', 5),
        ('24 متری', 'rectangular', 6.00, 4.00, None, 24.0000, False, 'even', 6),
        ('کناره 4×1', 'runner', 4.00, 1.00, None, 4.0000, False, 'even', 10),
        ('کناره 3×1', 'runner', 3.00, 1.00, None, 3.0000, False, 'even', 11),
        ('کناره 2×1', 'runner', 2.00, 1.00, None, 2.0000, False, 'even', 12),
        ('قالیچه 2.25×1.50', 'rectangular', 2.25, 1.50, None, 3.3750, False, 'even', 20),
        ('قالیچه 1.50×1', 'rectangular', 1.50, 1.00, None, 1.5000, False, 'even', 21),
        ('پادری 0.85×0.50', 'doormat', 0.85, 0.50, None, 0.4250, False, 'even', 30),
        ('رویه پشتی 1×0.50', 'cushion', 1.00, 0.50, None, 0.5000, False, 'even', 31),
        ('گرد قطر 3', 'round', None, None, 3.00, round(math.pi * 1.5**2, 4), False, 'even', 40),
        ('گرد قطر 2', 'round', None, None, 2.00, round(math.pi * 1.0**2, 4), False, 'even', 41),
        ('گرد قطر 1.50', 'round', None, None, 1.50, round(math.pi * 0.75**2, 4), False, 'even', 42),
        ('گرد قطر 1', 'round', None, None, 1.00, round(math.pi * 0.5**2, 4), False, 'even', 43),
    ]

    for s in sizes:
        CarpetSize.objects.get_or_create(
            name=s[0],
            defaults={
                'size_type': s[1],
                'length': s[2],
                'width': s[3],
                'diameter': s[4],
                'area': s[5],
                'is_nine_meter': s[6],
                'default_order_rule': s[7],
                'sort_order': s[8],
                'is_active': True,
            }
        )


def add_default_colors(apps, schema_editor):
    BackgroundColor = apps.get_model('catalog', 'BackgroundColor')
    colors = [
        ('کرم', 'کرم', '#F5F5DC', 1),
        ('سرمه‌ای', 'سرمه-ای', '#1A237E', 2),
        ('آبی', 'آبی', '#1565C0', 3),
        ('لاکی', 'لاکی', '#B71C1C', 4),
        ('روناسی', 'روناسی', '#880E4F', 5),
        ('دلفینی', 'دلفینی', '#4A148C', 6),
        ('دودی', 'دودی', '#616161', 7),
        ('گردویی', 'گردویی', '#5D4037', 8),
        ('نقره‌ای', 'نقره-ای', '#9E9E9E', 9),
        ('بادامی', 'بادامی', '#8D6E63', 10),
        ('یاسی', 'یاسی', '#9575CD', 11),
        ('بنفش', 'بنفش', '#7B1FA2', 12),
        ('سبز', 'سبز', '#2E7D32', 13),
        ('طلایی', 'طلایی', '#F9A825', 14),
        ('سفید', 'سفید', '#FAFAFA', 15),
        ('مشکی', 'مشکی', '#212121', 16),
        ('فیلی', 'فیلی', '#78909C', 17),
        ('آبی آسمانی', 'آبی-آسمانی', '#039BE5', 18),
    ]
    for c in colors:
        BackgroundColor.objects.get_or_create(
            name=c[0],
            defaults={'slug': c[1], 'color_code': c[2], 'sort_order': c[3]}
        )


def add_default_design_types(apps, schema_editor):
    DesignType = apps.get_model('catalog', 'DesignType')
    designs = [
        'افشان', 'خشتی', 'لچک و ترنج', 'سنتی', 'وینتیج', 'کلاسیک',
        'پتینه', 'فانتزی', 'کودک', 'آشپزخانه', 'طلاکوب',
        'ریزماهی', 'لاکچری', 'خاص', 'مدرن', 'ساده',
    ]
    for i, d in enumerate(designs, 1):
        slug = d.replace(' ', '-').replace('و-', 'و')
        DesignType.objects.get_or_create(name=d, defaults={'slug': slug, 'sort_order': i})


def add_default_weave_types(apps, schema_editor):
    WeaveType = apps.get_model('catalog', 'WeaveType')
    WeaveType.objects.get_or_create(name='بافتی', defaults={'slug': 'بافتی'})
    WeaveType.objects.get_or_create(name='چاپی (کلاریس)', defaults={'slug': 'چاپی-کلاریس'})


def add_default_features(apps, schema_editor):
    Feature = apps.get_model('catalog', 'Feature')
    Feature.objects.get_or_create(name='گل‌برجسته', defaults={'slug': 'گل-برجسته'})
    Feature.objects.get_or_create(name='ساده', defaults={'slug': 'ساده'})
    Feature.objects.get_or_create(name='برجسته', defaults={'slug': 'برجسته'})


def add_default_color_tones(apps, schema_editor):
    ColorTone = apps.get_model('catalog', 'ColorTone')
    tones = [('روشن', 'روشن'), ('تیره', 'تیره'), ('گرم', 'گرم'), ('سرد', 'سرد')]
    for t in tones:
        ColorTone.objects.get_or_create(name=t[0], defaults={'slug': t[1]})


def reverse_all(apps, schema_editor):
    """در صورت rollback هیچ کاری نمی‌کنیم"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_backgroundcolor_carpetsize_colortone_designtype_and_more'),
    ]

    operations = [
        migrations.RunPython(add_default_sizes, reverse_all),
        migrations.RunPython(add_default_colors, reverse_all),
        migrations.RunPython(add_default_design_types, reverse_all),
        migrations.RunPython(add_default_weave_types, reverse_all),
        migrations.RunPython(add_default_features, reverse_all),
        migrations.RunPython(add_default_color_tones, reverse_all),
    ]
