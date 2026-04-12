"""ایجاد منوها و ویجت‌های پیش‌فرض"""
from django.db import migrations


def create_defaults(apps, schema_editor):
    MenuItem = apps.get_model('appearance', 'MenuItem')
    FooterWidget = apps.get_model('appearance', 'FooterWidget')

    # منوی هدر
    header_items = [
        {'title': 'فروشگاه', 'link': '/farsh/', 'icon': 'bi-shop', 'position': 'header', 'order': 1},
        {'title': 'گالری تصاویر', 'link': '/gallery/images/', 'icon': 'bi-images', 'position': 'header', 'order': 2},
        {'title': 'گالری ویدیو', 'link': '/gallery/videos/', 'icon': 'bi-play-circle', 'position': 'header', 'order': 3},
        {'title': 'بلاگ', 'link': '/blog/', 'icon': 'bi-journal-richtext', 'position': 'header', 'order': 4},
        {'title': 'تماس با ما', 'link': '/page/contact-us/', 'icon': 'bi-telephone', 'position': 'header', 'order': 5},
    ]
    for item in header_items:
        if not MenuItem.objects.filter(title=item['title'], position=item['position']).exists():
            MenuItem.objects.create(**item)

    # منوی فوتر
    footer_items = [
        {'title': 'درباره ما', 'link': '/page/about-us/', 'position': 'footer', 'order': 1},
        {'title': 'نحوه خرید', 'link': '/page/how-to-buy/', 'position': 'footer', 'order': 2},
        {'title': 'شرایط ارسال', 'link': '/page/shipping-policy/', 'position': 'footer', 'order': 3},
        {'title': 'خرید اقساطی', 'link': '/page/installment-policy/', 'position': 'footer', 'order': 4},
        {'title': 'سوالات متداول', 'link': '/page/faq/', 'position': 'footer', 'order': 5},
        {'title': 'حریم خصوصی', 'link': '/page/privacy-policy/', 'position': 'footer', 'order': 6},
        {'title': 'قوانین', 'link': '/page/terms/', 'position': 'footer', 'order': 7},
    ]
    for item in footer_items:
        if not MenuItem.objects.filter(title=item['title'], position=item['position']).exists():
            MenuItem.objects.create(**item)

    # ویجت‌های فوتر
    widgets = [
        {'title': 'همیار فرش', 'widget_type': 'text', 'column': 1, 'order': 1,
         'content': 'فروشگاه آنلاین فرش ماشینی با امکان خرید نقدی و اقساطی. ارسال به سراسر ایران.'},
        {'title': 'دسترسی سریع', 'widget_type': 'links', 'column': 2, 'order': 1, 'content': ''},
        {'title': 'ارتباط با ما', 'widget_type': 'contact', 'column': 3, 'order': 1, 'content': ''},
        {'title': 'ما را دنبال کنید', 'widget_type': 'social', 'column': 4, 'order': 1, 'content': ''},
    ]
    for w in widgets:
        if not FooterWidget.objects.filter(title=w['title']).exists():
            FooterWidget.objects.create(**w)

    print("  -> منوها و ویجت‌های پیش‌فرض ایجاد شدند")


class Migration(migrations.Migration):
    dependencies = [
        ('appearance', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_defaults, migrations.RunPython.noop),
    ]
