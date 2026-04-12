from django import forms
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        exclude = ('updated_at',)
        widgets = {
            # اطلاعات سایت
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            
            # اطلاعات تماس
            'phone': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'telegram_id': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'instagram_id': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'eitaa_id': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'bale_id': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # تنظیمات تصویر
            'thumbnail_width': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'thumbnail_height': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'featured_image_size': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'info_bar_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'featured_line1_template': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'featured_line2_template': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            'featured_line3_template': forms.TextInput(attrs={'class': 'form-control', 'dir': 'rtl'}),
            
            # تنظیمات قیمت‌گذاری
            'profit_percent': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'rounding_step': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            
            # تنظیمات سفارش
            'free_shipping_min': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'deposit_percent': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'cancellation_fee_percent': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            
            # تنظیمات اقساط - ✅ اصلاح شده
            'installment_max': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'check_max_months': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'beta_max_months': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'check_monthly_interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'beta_monthly_interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'check_prepay_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'beta_prepay_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # تنظیمات SEO
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'seo_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'product_desc_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
