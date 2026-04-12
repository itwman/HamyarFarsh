"""
فرم‌های سفارش و سبد خرید
"""
from django import forms
from .models import Order, OrderItem
from accounts.models import Address
from catalog.models import CarpetSize
from products.models import Product


class AddToCartForm(forms.Form):
    """فرم افزودن به سبد خرید"""
    
    product_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    size_id = forms.IntegerField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'size-select'
        }),
        label='انتخاب سایز'
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'id': 'quantity-input'
        }),
        label='تعداد'
    )
    is_pair = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is-pair-checkbox'
        }),
        label='سفارش زوجی'
    )
    
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if product:
            # تنظیم انتخاب سایزها
            self.fields['size_id'].widget = forms.Select(
                choices=[(size.id, f"{size.name} - {size.get_display_price(product):,} تومان") 
                         for size in CarpetSize.objects.all()],
                attrs={'class': 'form-select', 'id': 'size-select'}
            )
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity', 1)
        is_pair = cleaned_data.get('is_pair', False)
        
        # بررسی زوج بودن تعداد
        if is_pair and quantity % 2 != 0:
            raise forms.ValidationError('برای سفارش زوجی، تعداد باید زوج باشد.')
        
        return cleaned_data


class CustomSizeOrderForm(forms.Form):
    """فرم سفارش سایز سفارشی"""
    
    product_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    length = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0.5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 4.5',
            'step': '0.01'
        }),
        label='طول (متر)'
    )
    width = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0.5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 3.5',
            'step': '0.01'
        }),
        label='عرض (متر)'
    )
    quantity = forms.IntegerField(
        min_value=2,
        initial=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '2',
            'step': '2'
        }),
        label='تعداد (زوج الزامی)',
        help_text='سایز سفارشی باید زوج سفارش داده شود'
    )
    customer_phone = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09xxxxxxxxx',
            'dir': 'ltr'
        }),
        label='شماره تماس'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات تکمیلی (اختیاری)'
        }),
        label='توضیحات'
    )
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity % 2 != 0:
            raise forms.ValidationError('سایز سفارشی باید به تعداد زوج سفارش داده شود.')
        return quantity
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        if not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError('شماره موبایل معتبر وارد کنید (09xxxxxxxxx)')
        return phone


class CheckoutForm(forms.Form):
    """فرم تکمیل سفارش"""
    
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='روش پرداخت'
    )
    shipping_address_id = forms.IntegerField(
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='آدرس ارسال'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات تکمیلی سفارش (اختیاری)'
        }),
        label='یادداشت'
    )
    
    # فیلدهای اقساط (اختیاری)
    installment_months = forms.IntegerField(
        required=False,
        min_value=2,
        max_value=18,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '2',
            'max': '18'
        }),
        label='تعداد ماه (اقساطی)'
    )
    down_payment = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'پیش‌پرداخت (تومان)'
        }),
        label='پیش‌پرداخت (اختیاری)'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # تنظیم انتخاب آدرس‌ها
            addresses = Address.objects.filter(user=user)
            self.fields['shipping_address_id'].widget = forms.RadioSelect(
                choices=[(addr.id, addr.get_full_address()) for addr in addresses],
                attrs={'class': 'form-check-input'}
            )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        installment_months = cleaned_data.get('installment_months')
        
        # بررسی اقساط
        if payment_method in ['installment_check', 'installment_beta']:
            if not installment_months:
                raise forms.ValidationError('برای خرید اقساطی باید تعداد ماه را انتخاب کنید.')
            
            # چک: حداکثر 12 ماه
            if payment_method == 'installment_check' and installment_months > 12:
                raise forms.ValidationError('خرید اقساطی چکی حداکثر 12 ماه است.')
            
            # بتا: حداکثر 18 ماه
            if payment_method == 'installment_beta' and installment_months > 18:
                raise forms.ValidationError('خرید اقساطی بتا حداکثر 18 ماه است.')
        
        return cleaned_data


class OrderAdminForm(forms.ModelForm):
    """فرم مدیریت سفارش"""
    
    class Meta:
        model = Order
        fields = ['status', 'payment_method', 'admin_notes', 
                  'final_price_at_delivery', 'shipping_cost']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'final_price_at_delivery': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }
