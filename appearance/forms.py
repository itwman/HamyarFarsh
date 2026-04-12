from django import forms
from .models import MenuItem, FooterWidget


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['title', 'link', 'icon', 'position', 'parent', 'order',
                  'is_active', 'target_blank', 'css_class']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr', 'placeholder': '/page/about-us/'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-house'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'css_class': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فقط آیتم‌های بدون والد رو به‌عنوان والد نشون بده
        self.fields['parent'].queryset = MenuItem.objects.filter(parent__isnull=True)
        self.fields['parent'].required = False


class FooterWidgetForm(forms.ModelForm):
    class Meta:
        model = FooterWidget
        fields = ['title', 'widget_type', 'content', 'column', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'widget_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                             'placeholder': 'محتوای ویجت...'}),
            'column': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4, 'style': 'width:80px;'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
        }
