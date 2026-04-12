"""
ماشین‌حساب اقساط
محاسبه چک صیادی و طرح بتا
"""
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class InstallmentCalculator:
    """ماشین‌حساب اقساط"""
    
    def __init__(self, total_amount, down_payment=0, interest_rate=2.5, 
                 num_installments=12, period='monthly'):
        """
        Args:
            total_amount: مبلغ کل فاکتور (تومان)
            down_payment: پیش‌پرداخت (تومان)
            interest_rate: نرخ سود ماهانه (درصد)
            num_installments: تعداد اقساط
            period: دوره پرداخت ('monthly' یا 'bimonthly')
        """
        self.total_amount = Decimal(str(total_amount))
        self.down_payment = Decimal(str(down_payment))
        self.interest_rate = Decimal(str(interest_rate))
        self.num_installments = num_installments
        self.period = period
    
    def calculate(self):
        """محاسبه کامل اقساط"""
        # مبلغ قابل اقساط
        financed_amount = self.total_amount - self.down_payment
        
        # تعداد ماه‌های واقعی
        months = self.num_installments if self.period == 'monthly' else self.num_installments * 2
        
        # محاسبه سود
        total_interest = financed_amount * (self.interest_rate / 100) * months
        
        # مبلغ کل با سود
        total_with_interest = financed_amount + total_interest
        
        # مبلغ هر قسط
        installment_amount = int(total_with_interest / self.num_installments)
        
        # قسط آخر (اختلاف رند شدن)
        last_installment = int(total_with_interest - (installment_amount * (self.num_installments - 1)))
        
        return {
            'total_amount': float(self.total_amount),
            'down_payment': float(self.down_payment),
            'financed_amount': float(financed_amount),
            'interest_rate': float(self.interest_rate),
            'total_months': months,
            'total_interest': float(total_interest),
            'total_with_interest': float(total_with_interest),
            'num_installments': self.num_installments,
            'installment_amount': installment_amount,
            'last_installment': last_installment,
            'period': self.period,
        }
    
    def generate_schedule(self, first_due_date=None):
        """
        تولید برنامه زمانی اقساط
        
        Args:
            first_due_date: تاریخ سررسید اولین قسط (date object)
        
        Returns:
            list: لیست اقساط با تاریخ سررسید
        """
        calc_result = self.calculate()
        installment_amount = calc_result['installment_amount']
        last_installment = calc_result['last_installment']
        
        # تاریخ شروع
        if first_due_date is None:
            first_due_date = date.today() + timedelta(days=30)
        
        schedule = []
        current_date = first_due_date
        
        for i in range(1, self.num_installments + 1):
            amount = last_installment if i == self.num_installments else installment_amount
            
            schedule.append({
                'number': i,
                'amount': amount,
                'due_date': current_date,
            })
            
            # محاسبه تاریخ قسط بعدی
            if self.period == 'monthly':
                current_date = current_date + relativedelta(months=1)
            else:  # bimonthly
                current_date = current_date + relativedelta(months=2)
        
        return schedule


def calculate_check_installment(total_amount, down_payment, num_installments, 
                                interest_rate, period='monthly'):
    """محاسبه اقساط چکی"""
    calc = InstallmentCalculator(
        total_amount=total_amount,
        down_payment=down_payment,
        interest_rate=interest_rate,
        num_installments=num_installments,
        period=period
    )
    return calc.calculate()


def calculate_beta_installment(total_amount, down_payment, num_installments, 
                               interest_rate, period='monthly'):
    """محاسبه اقساط بتا (بازنشستگان بانک رفاه) - حداکثر 18 ماه"""
    if num_installments > 18:
        raise ValueError('طرح بتا حداکثر 18 ماه است')
    
    calc = InstallmentCalculator(
        total_amount=total_amount,
        down_payment=down_payment,
        interest_rate=interest_rate,
        num_installments=num_installments,
        period=period
    )
    return calc.calculate()


def check_installment_eligibility(total_amount, max_installment_amount):
    """بررسی واجد شرایط بودن برای اقساط"""
    total_amount = Decimal(str(total_amount))
    max_installment = Decimal(str(max_installment_amount))
    
    if total_amount <= max_installment:
        return {
            'eligible': True,
            'installment_amount': float(total_amount),
            'cash_amount': 0,
            'message': 'کل مبلغ قابل اقساط است'
        }
    else:
        cash_amount = total_amount - max_installment
        return {
            'eligible': True,
            'installment_amount': float(max_installment),
            'cash_amount': float(cash_amount),
            'message': f'حداکثر {max_installment:,} تومان قابل اقساط است. مابقی ({cash_amount:,} تومان) باید نقدی پرداخت شود.'
        }
