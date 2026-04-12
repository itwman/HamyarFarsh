from django import forms
from .models import Ticket, TicketReply


class ChatStartForm(forms.Form):
    """فرم شروع چت"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': 'نام شما'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': 'موبایل (اختیاری)', 'dir': 'ltr'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control form-control-sm', 'rows': 2, 'placeholder': 'پیام شما...'
    }))


class TicketForm(forms.ModelForm):
    """فرم ایجاد تیکت"""
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 5, 'placeholder': 'شرح مشکل یا درخواست شما...'
    }), label='متن پیام')

    class Meta:
        model = Ticket
        fields = ['subject', 'department', 'priority', 'order']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع تیکت'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False
        if user:
            from orders.models import Order
            self.fields['order'].queryset = Order.objects.filter(customer=user).order_by('-created_at')[:20]
        else:
            self.fields['order'].queryset = Order.objects.none()


class TicketReplyForm(forms.Form):
    """فرم پاسخ به تیکت"""
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 4, 'placeholder': 'پاسخ شما...'
    }))
    attachment = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control', 'accept': 'image/*,.pdf,.doc,.docx,.zip'
    }))


class AdminReplyForm(forms.Form):
    """فرم پاسخ مدیر"""
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 4, 'placeholder': 'پاسخ مدیر...'
    }))
    status = forms.ChoiceField(choices=Ticket.Status.choices, widget=forms.Select(attrs={
        'class': 'form-select'
    }), label='تغییر وضعیت')
