"""
ماژول ارسال پیامک با استفاده از سرویس sms.ir
مستندات API: https://sms.ir/
"""
import requests
import logging
from django.conf import settings
from settings_app.models import SiteSettings

logger = logging.getLogger(__name__)


class SMSService:
    """کلاس سرویس ارسال پیامک از طریق sms.ir"""
    
    BASE_URL = "https://api.sms.ir/v1"
    
    def __init__(self):
        """دریافت تنظیمات از دیتابیس"""
        site_settings = SiteSettings.get_solo()
        self.api_key = site_settings.sms_api_key
        self.sender = site_settings.sms_sender
        self.enabled = site_settings.sms_enabled
    
    def _get_headers(self):
        """ساخت header های مورد نیاز برای درخواست API"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
    
    def send_sms(self, mobile, message):
        """
        ارسال پیامک ساده
        
        Args:
            mobile (str): شماره موبایل گیرنده (مثال: 09123456789)
            message (str): متن پیامک
            
        Returns:
            dict: نتیجه ارسال شامل وضعیت و message_id
        """
        if not self.enabled:
            logger.warning("SMS service is disabled in settings")
            return {'success': False, 'error': 'سرویس پیامک غیرفعال است'}
        
        if not self.api_key:
            logger.error("SMS API key is not configured")
            return {'success': False, 'error': 'API Key تنظیم نشده است'}
        
        if not self.sender:
            logger.error("SMS sender number is not configured")
            return {'success': False, 'error': 'شماره فرستنده تنظیم نشده است'}
        
        url = f"{self.BASE_URL}/send/bulk"
        
        payload = {
            "lineNumber": self.sender,
            "messageText": message,
            "mobiles": [mobile] if isinstance(mobile, str) else mobile
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"SMS sent successfully to {mobile}")
                return {
                    'success': True,
                    'message_id': data.get('data', {}).get('messageId'),
                    'cost': data.get('data', {}).get('cost')
                }
            else:
                error_msg = response.json().get('message', 'خطای نامشخص')
                logger.error(f"SMS sending failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            logger.error("SMS API request timeout")
            return {'success': False, 'error': 'زمان اتصال به سرویس پیامک به پایان رسید'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"SMS API request failed: {str(e)}")
            return {'success': False, 'error': f'خطا در اتصال: {str(e)}'}
        
        except Exception as e:
            logger.error(f"Unexpected error in SMS sending: {str(e)}")
            return {'success': False, 'error': f'خطای غیرمنتظره: {str(e)}'}
    
    def send_verification_code(self, mobile, code):
        """
        ارسال کد تأیید (از الگوی از پیش تعریف شده)
        
        Args:
            mobile (str): شماره موبایل
            code (str): کد تأیید
            
        Returns:
            dict: نتیجه ارسال
        """
        url = f"{self.BASE_URL}/send/verify"
        
        payload = {
            "mobile": mobile,
            "templateId": 100000,  # شماره الگوی کد تأیید در پنل sms.ir
            "parameters": [
                {
                    "name": "CODE",
                    "value": code
                }
            ]
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'message_id': data.get('data', {}).get('messageId')
                }
            else:
                return {
                    'success': False,
                    'error': response.json().get('message', 'خطا در ارسال'),
                    'status_code': response.status_code
                }
        
        except Exception as e:
            logger.error(f"Error sending verification code: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_credit(self):
        """
        دریافت اعتبار باقیمانده حساب
        
        Returns:
            dict: اطلاعات اعتبار
        """
        if not self.api_key:
            return {'success': False, 'error': 'API Key تنظیم نشده است'}
        
        url = f"{self.BASE_URL}/credit"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'credit': data.get('data', {}).get('credit', 0)
                }
            else:
                return {
                    'success': False,
                    'error': 'خطا در دریافت اعتبار',
                    'status_code': response.status_code
                }
        
        except Exception as e:
            logger.error(f"Error getting credit: {str(e)}")
            return {'success': False, 'error': str(e)}


# توابع کمکی برای استفاده آسان‌تر
def send_sms(mobile, message):
    """ارسال پیامک ساده"""
    service = SMSService()
    return service.send_sms(mobile, message)


def send_verification_code(mobile, code):
    """ارسال کد تأیید"""
    service = SMSService()
    return service.send_verification_code(mobile, code)


def get_sms_credit():
    """دریافت اعتبار"""
    service = SMSService()
    return service.get_credit()


# قالب‌های پیامک برای سفارشات
class OrderSMSTemplates:
    """قالب‌های پیامک برای مراحل مختلف سفارش"""
    
    @staticmethod
    def order_placed(customer_name, order_id, total_amount):
        """پیامک ثبت سفارش"""
        return f"""
{customer_name} عزیز
سفارش شما با شماره #{order_id} به مبلغ {total_amount:,} تومان ثبت شد.
با تشکر - همیار فرش
        """.strip()
    
    @staticmethod
    def order_confirmed(customer_name, order_id):
        """پیامک تأیید سفارش"""
        return f"""
{customer_name} عزیز
سفارش #{order_id} شما تأیید و در حال آماده‌سازی است.
همیار فرش
        """.strip()
    
    @staticmethod
    def order_shipped(customer_name, order_id, tracking_code=None):
        """پیامک ارسال سفارش"""
        msg = f"{customer_name} عزیز\nسفارش #{order_id} شما ارسال شد."
        if tracking_code:
            msg += f"\nکد پیگیری: {tracking_code}"
        msg += "\nهمیار فرش"
        return msg
    
    @staticmethod
    def order_delivered(customer_name, order_id):
        """پیامک تحویل سفارش"""
        return f"""
{customer_name} عزیز
سفارش #{order_id} شما تحویل داده شد.
از خرید شما متشکریم.
همیار فرش
        """.strip()


def send_order_sms(mobile, sms_type, **kwargs):
    """
    ارسال پیامک سفارش بر اساس نوع
    
    Args:
        mobile (str): شماره موبایل مشتری
        sms_type (str): نوع پیامک (placed, confirmed, shipped, delivered)
        **kwargs: پارامترهای مورد نیاز برای هر نوع پیامک
    
    Returns:
        dict: نتیجه ارسال
    """
    templates = {
        'placed': OrderSMSTemplates.order_placed,
        'confirmed': OrderSMSTemplates.order_confirmed,
        'shipped': OrderSMSTemplates.order_shipped,
        'delivered': OrderSMSTemplates.order_delivered,
    }
    
    if sms_type not in templates:
        return {'success': False, 'error': 'نوع پیامک نامعتبر است'}
    
    try:
        message = templates[sms_type](**kwargs)
        return send_sms(mobile, message)
    except Exception as e:
        logger.error(f"Error creating SMS message: {str(e)}")
        return {'success': False, 'error': f'خطا در ساخت پیامک: {str(e)}'}
