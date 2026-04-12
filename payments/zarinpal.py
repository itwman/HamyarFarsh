import requests
from typing import Dict


class ZarinpalGateway:
    """کلاس اتصال به درگاه زرین‌پال"""
    
    SANDBOX_URL = 'https://sandbox.zarinpal.com/pg/v4/payment/'
    PRODUCTION_URL = 'https://payment.zarinpal.com/pg/v4/payment/'
    
    def __init__(self, merchant_id: str, sandbox: bool = False):
        self.merchant_id = merchant_id
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
    
    def payment_request(self, amount: int, description: str, callback_url: str, 
                       mobile: str = None, email: str = None) -> Dict:
        """
        ایجاد درخواست پرداخت
        
        Args:
            amount: مبلغ به تومان
            description: توضیحات تراکنش
            callback_url: آدرس بازگشت
            mobile: شماره موبایل (اختیاری)
            email: ایمیل (اختیاری)
        
        Returns:
            dict: {'status': 'success', 'authority': '...', 'payment_url': '...'} یا
                  {'status': 'error', 'message': '...'}
        """
        url = self.base_url + 'request.json'
        
        data = {
            'merchant_id': self.merchant_id,
            'amount': amount,
            'description': description,
            'callback_url': callback_url,
        }
        
        if mobile:
            data['mobile'] = mobile
        if email:
            data['email'] = email
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                authority = result['data']['authority']
                payment_url = f'{self.base_url.replace("/v4/payment/", "/StartPay/")}{authority}'
                
                return {
                    'status': 'success',
                    'authority': authority,
                    'payment_url': payment_url
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('errors', {}).get('message', 'خطای ناشناخته')
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'خطا در اتصال به درگاه: {str(e)}'
            }
    
    def payment_verify(self, authority: str, amount: int) -> Dict:
        """
        تأیید پرداخت
        
        Args:
            authority: شناسه تراکنش دریافتی از درگاه
            amount: مبلغ به تومان
        
        Returns:
            dict: {'status': 'success', 'ref_id': '...', 'card_pan': '...'} یا
                  {'status': 'error', 'message': '...'}
        """
        url = self.base_url + 'verify.json'
        
        data = {
            'merchant_id': self.merchant_id,
            'authority': authority,
            'amount': amount,
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') in [100, 101]:  # 100=موفق, 101=قبلاً تأیید شده
                return {
                    'status': 'success',
                    'ref_id': result['data']['ref_id'],
                    'card_pan': result['data'].get('card_pan', ''),
                    'card_hash': result['data'].get('card_hash', ''),
                    'fee_type': result['data'].get('fee_type', ''),
                    'fee': result['data'].get('fee', 0),
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('errors', {}).get('message', 'تأیید پرداخت ناموفق بود')
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'خطا در تأیید پرداخت: {str(e)}'
            }
