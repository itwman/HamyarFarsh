from django import forms
from .models import Coupon


class CouponForm(forms.ModelForm):
    """فرم ایجاد/ویرایش کوپن"""
    class Meta:
        model = Coupon
        fields = ['code', 'coupon_type', 'amount', 'max_discount', 'min_order_amount',
                  'max_usage_total', 'max_usage_per_user', 'limited_to_products',
                  'limited_to_categories', 'start_date', 'end_date', 'is_active', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr',
                                           'style': 'text-transform:uppercase;font-weight:bold;letter-spacing:2px;'}),
            'coupon_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control',
                                                      'placeholder': 'خالی = بدون سقف'}),
            'min_order_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_usage_total': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:100px;'}),
            'max_usage_per_user': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:100px;'}),
            'limited_to_products': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'limited_to_categories': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'توضیح داخلی...'}),
        }


class CouponApplyForm(forms.Form):
    """فرم اعمال کوپن در سبد خرید"""
    code = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'dir': 'ltr',
            'placeholder': 'کد تخفیف را وارد کنید',
            'style': 'text-transform:uppercase;',
        })
    )
