"""
سیستم تولید فاکتور
مدیریت قیمت روز و جریمه انصراف
"""
from decimal import Decimal
from datetime import datetime
import jdatetime


class InvoiceGenerator:
    """کلاس تولید فاکتور"""
    
    def __init__(self, order):
        """
        Args:
            order: شیء Order از Django
        """
        self.order = order
    
    def generate_html(self):
        """تولید HTML فاکتور"""
        from django.template.loader import render_to_string
        
        context = {
            'order': self.order,
            'items': self.order.items.all(),
            'today': jdatetime.date.today(),
            'subtotal': self.order.get_subtotal(),
            'shipping_cost': self.order.get_shipping_cost(),
            'total': self.order.total_amount,
            'paid': self.order.paid_amount,
            'remaining': self.order.total_amount - self.order.paid_amount,
        }
        
        return render_to_string('orders/invoice.html', context)
    
    def generate_pdf(self):
        """تولید PDF فاکتور"""
        # TODO: استفاده از ReportLab یا WeasyPrint
        pass


class PriceUpdateManager:
    """مدیریت بروزرسانی قیمت"""
    
    @staticmethod
    def calculate_price_difference(order):
        """
        محاسبه تفاوت قیمت روز با قیمت ثبت سفارش
        
        Args:
            order: شیء Order
        
        Returns:
            dict: {
                'old_total': مبلغ قدیم,
                'new_total': مبلغ جدید,
                'difference': تفاوت,
                'items_changes': لیست تغییرات آیتم‌ها
            }
        """
        old_total = order.total_amount
        new_total = Decimal('0')
        items_changes = []
        
        for item in order.items.all():
            # قیمت قدیم
            old_price = item.price
            
            # قیمت جدید (روز)
            if item.is_custom_size:
                # سایز سفارشی - محاسبه جداگانه
                new_price = old_price  # فعلاً بدون تغییر
            else:
                # قیمت روز از محصول
                new_price = item.product.get_price_for_size(item.carpet_size)
            
            # محاسبه تفاوت
            difference = new_price - old_price
            quantity_total_diff = difference * item.quantity
            
            items_changes.append({
                'item': item,
                'old_price': float(old_price),
                'new_price': float(new_price),
                'difference': float(difference),
                'quantity': item.quantity,
                'total_difference': float(quantity_total_diff),
            })
            
            new_total += new_price * item.quantity
        
        # هزینه ارسال
        new_total += order.get_shipping_cost()
        
        return {
            'old_total': float(old_total),
            'new_total': float(new_total),
            'difference': float(new_total - old_total),
            'items_changes': items_changes,
        }
    
    @staticmethod
    def apply_price_update(order):
        """
        اعمال قیمت روز به سفارش
        
        فقط برای سفارش‌های پرداخت موقع تحویل
        بیعانه ثابت می‌ماند
        """
        if order.payment_method != 'deposit_on_delivery':
            raise ValueError('فقط برای سفارش‌های پرداخت موقع تحویل')
        
        # محاسبه قیمت‌های جدید
        price_data = PriceUpdateManager.calculate_price_difference(order)
        
        # بروزرسانی آیتم‌ها
        for change in price_data['items_changes']:
            item = change['item']
            item.price = Decimal(str(change['new_price']))
            item.save()
        
        # بروزرسانی مبلغ کل
        order.total_amount = Decimal(str(price_data['new_total']))
        order.save()
        
        return price_data


class CancellationFeeCalculator:
    """محاسبه جریمه انصراف"""
    
    @staticmethod
    def calculate_fee(order):
        """
        محاسبه جریمه انصراف
        
        قوانین:
        - 50% بیعانه
        - + هزینه ایاب و ذهاب
        
        Args:
            order: شیء Order
        
        Returns:
            dict: {
                'deposit': بیعانه,
                'penalty': جریمه (50% بیعانه),
                'shipping_both_ways': ایاب و ذهاب,
                'total_fee': جمع جریمه,
                'refund_amount': مبلغ قابل برگشت
            }
        """
        deposit = order.paid_amount
        penalty = deposit * Decimal('0.5')  # 50%
        shipping_cost = order.get_shipping_cost()
        shipping_both_ways = shipping_cost * 2
        
        total_fee = penalty + shipping_both_ways
        refund_amount = deposit - total_fee
        
        return {
            'deposit': float(deposit),
            'penalty': float(penalty),
            'shipping_cost': float(shipping_cost),
            'shipping_both_ways': float(shipping_both_ways),
            'total_fee': float(total_fee),
            'refund_amount': float(max(refund_amount, 0)),
        }
    
    @staticmethod
    def process_cancellation(order, reason=''):
        """
        پردازش انصراف از سفارش
        
        Args:
            order: شیء Order
            reason: دلیل انصراف
        """
        if order.status == 'cancelled':
            raise ValueError('این سفارش قبلاً لغو شده است')
        
        # محاسبه جریمه
        fee_data = CancellationFeeCalculator.calculate_fee(order)
        
        # تغییر وضعیت
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.cancellation_fee = Decimal(str(fee_data['total_fee']))
        order.refund_amount = Decimal(str(fee_data['refund_amount']))
        order.cancelled_at = datetime.now()
        order.save()
        
        return fee_data


def generate_invoice_number(order_id):
    """
    تولید شماره فاکتور
    
    فرمت: INV-YYYYMM-XXXXX
    مثال: INV-140312-00042
    """
    today = jdatetime.date.today()
    year_month = today.strftime('%y%m')
    order_num = str(order_id).zfill(5)
    
    return f'INV-{year_month}-{order_num}'
