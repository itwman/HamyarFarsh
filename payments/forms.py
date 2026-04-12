from django import forms
from .models import InstallmentPlan, Installment
from django.core.exceptions import ValidationError


class InstallmentPlanForm(forms.ModelForm):
    """فرم ایجاد طرح اقساط"""
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'plan_type', 'total_amount', 'down_payment', 
            'interest_rate', 'num_installments', 'period', 'first_due_date'
        ]
        widgets = {
            'plan_type': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'down_payment': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'num_installments': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 18}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'first_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'plan_type': 'نوع طرح اقساط',
            'total_amount': 'مبلغ کل فاکتور (تومان)',
            'down_payment': 'پیش‌پرداخت (تومان)',
            'interest_rate': 'نرخ سود ماهانه (%)',
            'num_installments': 'تعداد اقساط',
            'period': 'دوره پرداخت',
            'first_due_date': 'تاریخ سررسید اولین قسط',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get('total_amount')
        down_payment = cleaned_data.get('down_payment', 0)
        plan_type = cleaned_data.get('plan_type')
        num_installments = cleaned_data.get('num_installments')
        
        # بررسی سقف اقساط
        from settings_app.models import SiteSettings
        settings = SiteSettings.get_solo()
        
        if total_amount and total_amount > settings.installment_max:
            raise ValidationError(
                f'حداکثر مبلغ قابل اقساط {settings.installment_max:,} تومان است. '
                f'مبلغ اضافی باید نقدی پرداخت شود.'
            )
        
        # بررسی پیش‌پرداخت
        if down_payment and total_amount:
            if down_payment > total_amount:
                raise ValidationError('پیش‌پرداخت نمی‌تواند بیشتر از مبلغ کل باشد.')
        
        # بررسی تعداد اقساط بر اساس نوع طرح
        if plan_type == 'check' and num_installments and num_installments > 12:
            raise ValidationError('در طرح چک صیادی حداکثر 12 قسط مجاز است.')
        
        if plan_type == 'beta' and num_installments and num_installments > 18:
            raise ValidationError('در طرح بتا حداکثر 18 قسط مجاز است.')
        
        return cleaned_data


class InstallmentCalculatorForm(forms.Form):
    """فرم محاسبه‌گر اقساط برای مشتری"""
    
    PLAN_TYPE_CHOICES = [
        ('check', 'چک صیادی'),
        ('beta', 'طرح بتا (بانک رفاه)'),
    ]
    
    PERIOD_CHOICES = [
        ('monthly', 'ماهانه'),
        ('bimonthly', 'دوماهانه'),
    ]
    
    total_amount = forms.DecimalField(
        label='مبلغ کل (تومان)',
        max_digits=12,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 50000000'
        })
    )
    
    down_payment = forms.DecimalField(
        label='پیش‌پرداخت (تومان)',
        max_digits=12,
        decimal_places=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'اختیاری - مثال: 10000000'
        })
    )
    
    plan_type = forms.ChoiceField(
        label='نوع طرح',
        choices=PLAN_TYPE_CHOICES,
        initial='check',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    num_installments = forms.IntegerField(
        label='تعداد اقساط',
        min_value=1,
        max_value=18,
        initial=12,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    period = forms.ChoiceField(
        label='دوره پرداخت',
        choices=PERIOD_CHOICES,
        initial='monthly',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CheckDetailsForm(forms.ModelForm):
    """فرم ثبت جزئیات چک"""
    
    class Meta:
        model = Installment
        fields = ['check_number', 'bank_name']
        widgets = {
            'check_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره چک'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام بانک'
            }),
        }
        labels = {
            'check_number': 'شماره چک',
            'bank_name': 'نام بانک',
        }
