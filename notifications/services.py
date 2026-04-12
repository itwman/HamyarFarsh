"""
سرویس‌های اطلاع‌رسانی
- ارسال پیامک خودکار بر اساس رویداد
- ایجاد نوتیفیکیشن درون‌سایتی
"""
import requests
from django.conf import settings as django_settings
from settings_app.models import SiteSettings
from .models import Notification, SMSTemplate, SMSLog


def send_sms(phone, message, event=''):
    """ارسال پیامک با API"""
    ss = SiteSettings.get_solo()
    if not ss.sms_enabled or not ss.sms_api_key:
        # ذخیره لاگ ولی ارسال نکن
        SMSLog.objects.create(phone=phone, message=message, event=event,
                              status='failed', api_response='SMS disabled or no API key')
        return False

    try:
        # TODO: اینجا با API سرویس پیامکی جایگزین بشه
        # مثال برای Kavenegar:
        # resp = requests.get(f'https://api.kavenegar.com/v1/{ss.sms_api_key}/sms/send.json',
        #     params={'receptor': phone, 'message': message, 'sender': ss.sms_sender})
        # result = resp.json()

        SMSLog.objects.create(phone=phone, message=message, event=event,
                              status='sent', api_response='OK (mock)')
        return True
    except Exception as e:
        SMSLog.objects.create(phone=phone, message=message, event=event,
                              status='failed', api_response=str(e))
        return False


def notify_event(event, user=None, order=None, **extra):
    """
    ارسال اطلاع‌رسانی بر اساس رویداد
    - ایجاد نوتیفیکیشن درون‌سایتی
    - ارسال پیامک (اگر قالب فعال باشه)
    """
    ss = SiteSettings.get_solo()

    # آماده‌سازی متغیرها
    ctx = {
        'site_name': ss.site_name,
        'name': user.get_full_name() if user else '',
        'order_id': str(order.id) if order else '',
        'amount': f'{order.total_amount:,}' if order else '',
        'status': order.get_status_display_persian() if order else '',
    }
    ctx.update(extra)

    # --- نوتیفیکیشن درون‌سایتی ---
    notif_map = {
        'order_created': ('سفارش ثبت شد', f'سفارش شماره {ctx["order_id"]} با موفقیت ثبت شد.', 'order'),
        'order_confirmed': ('سفارش تأیید شد', f'سفارش شماره {ctx["order_id"]} تأیید شد.', 'order'),
        'order_shipped': ('سفارش ارسال شد', f'سفارش شماره {ctx["order_id"]} ارسال شد.', 'order'),
        'order_delivered': ('سفارش تحویل شد', f'سفارش شماره {ctx["order_id"]} تحویل داده شد.', 'order'),
        'payment_success': ('پرداخت موفق', f'پرداخت سفارش شماره {ctx["order_id"]} انجام شد.', 'payment'),
    }

    if user and event in notif_map:
        title, message, ntype = notif_map[event]
        link = f'/orders/order/{order.id}/' if order else ''
        Notification.create_for_user(user, title, message, notif_type=ntype, link=link)

    # --- پیامک خودکار ---
    try:
        tpl = SMSTemplate.objects.get(event=event, is_active=True)
        sms_text = tpl.render(**ctx)

        # ارسال به مشتری
        if user and hasattr(user, 'phone') and user.phone:
            send_sms(user.phone, sms_text, event=event)

        # ارسال به مدیر (فقط برای ثبت سفارش)
        if event == 'order_created':
            try:
                admin_tpl = SMSTemplate.objects.get(event='order_created_admin', is_active=True)
                admin_text = admin_tpl.render(**ctx)
                if ss.mobile:
                    send_sms(ss.mobile, admin_text, event='order_created_admin')
            except SMSTemplate.DoesNotExist:
                pass

    except SMSTemplate.DoesNotExist:
        pass
