from django import forms
from .models import HomeSlider, HomeBanner, HomeSection


class HomeSliderForm(forms.ModelForm):
    class Meta:
        model = HomeSlider
        fields = ['title', 'subtitle', 'button_text', 'button_link',
                  'image_desktop', 'image_mobile', 'text_color', 'overlay_opacity',
                  'order', 'is_active', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان اسلاید'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'زیرعنوان (اختیاری)'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: مشاهده محصولات'}),
            'button_link': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr', 'placeholder': '/farsh/'}),
            'image_desktop': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_mobile': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'text_color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'overlay_opacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'style': 'width:100px;'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = ['title', 'image', 'link', 'alt_text', 'position', 'width',
                  'order', 'is_active', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'width': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class HomeSectionForm(forms.ModelForm):
    class Meta:
        model = HomeSection
        fields = ['title', 'subtitle', 'icon', 'section_type', 'auto_filter', 'auto_comb',
                  'manual_products', 'html_content', 'item_count', 'bg_color',
                  'show_more_link', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-fire'}),
            'section_type': forms.Select(attrs={'class': 'form-select'}),
            'auto_filter': forms.Select(attrs={'class': 'form-select'}),
            'auto_comb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 1200'}),
            'manual_products': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
            'html_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'dir': 'ltr', 'style': 'font-family:monospace;'}),
            'item_count': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'bg_color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'show_more_link': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr', 'placeholder': '/farsh/'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
        }
