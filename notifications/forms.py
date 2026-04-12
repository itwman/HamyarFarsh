from django import forms
from .models import Announcement, SMSTemplate


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['text', 'link', 'link_text', 'bg_color', 'text_color', 'icon',
                  'dismissible', 'start_date', 'end_date', 'is_active', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'متن اعلان...'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'link_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مشاهده جزئیات'}),
            'bg_color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'text_color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-megaphone'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
        }


class SMSTemplateForm(forms.ModelForm):
    class Meta:
        model = SMSTemplate
        fields = ['event', 'template', 'is_active']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                              'placeholder': '{name} عزیز، سفارش شماره {order_id} ثبت شد.'}),
        }
