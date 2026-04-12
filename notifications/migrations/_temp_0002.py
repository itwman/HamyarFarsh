"""ایجاد قالب‌های پیامک پیش‌فرض"""
from django.db import migrations


def create_defaults(apps, schema_editor):
    SMSTemplate = apps.get_model('notifications', 'SMSTemplate')

    templates = [
        ('order_created', '{name} عزیز، سفارش شماره {order_id} به مبلغ {amount} تومان در {site_name} ثبت شد. با تشکر'),
        ('order_created_admin', 'سفارش جدید #{order_id} به مبلغ {amount} تومان از {name} ثبت شد.'),
        ('order_confirmed', '{name} عزیز، سفارش شماره {order_id} تأیید شد و در حال آماده‌سازی است. {site_name}'),
        ('order_shipped', '{name} عزیز، سفارش شماره {order_id} ارسال شد. {site_name}'),
        ('order_delivered', '{name} عزیز، سفارش شماره {order_id} تحویل داده شد. از خرید شما متشکریم. {site_name}'),
        ('payment_success', '{name} عزیز، پرداخت سفارش شماره {order_id} به مبلغ {amount} تومان با موفقیت انجام شد. {site_name}'),
        ('installment_due', '{name} عزیز، یادآوری: قسط سفارش شماره {order_id} به مبلغ {amount} تومان سررسید شده. {site_name}'),
    ]

    for event, template in templates:
        if not SMSTemplate.objects.filter(event=event).exists():
            SMSTemplate.objects.create(event=event, template=template, is_active=True)
            print(f"  -> قالب '{event}' ایجاد شد")


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_defaults, migrations.RunPython.noop),
    ]
