import re
from django import forms
from .models import NewsletterSubscriber, SMSCampaign


class SubscribeForm(forms.Form):
    """فرم عضویت خبرنامه — فوتر سایت"""
    phone = forms.CharField(
        max_length=11, min_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'dir': 'ltr', 'inputmode': 'numeric',
            'placeholder': '09xxxxxxxxx',
            'pattern': '09[0-9]{9}',
        }),
        error_messages={'required': 'شماره موبایل الزامی است.'}
    )
    name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام (اختیاری)'})
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('شماره موبایل نامعتبر است.')
        return phone


class SMSCampaignForm(forms.ModelForm):
    """فرم ایجاد/ویرایش کمپین"""
    class Meta:
        model = SMSCampaign
        fields = ['title', 'message', 'recipient_type', 'scheduled_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان کمپین'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': '{name} عزیز\nفروش ویژه فرش در {site_name}!\nتخفیف تا 30%\nhamyarfarsh.com'
            }),
            'recipient_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class BulkImportForm(forms.Form):
    """فرم واردکردن شماره از فایل"""
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.txt,.xlsx'}),
        help_text='فایل CSV یا TXT (هر شماره در یک خط) یا Excel'
    )


class BulkAddForm(forms.Form):
    """فرم افزودن دستی شماره‌ها"""
    phones = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 6, 'dir': 'ltr',
            'placeholder': '09121234567\n09131234567\n09141234567'
        }),
        help_text='هر شماره در یک خط'
    )
