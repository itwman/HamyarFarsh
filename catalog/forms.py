from django import forms
from .models import (
    Manufacturer, Album, BackgroundColor, DesignType,
    WeaveType, Feature, ColorTone, CarpetSize
)


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = (
            'name', 'slug', 'logo', 'phone', 'mobile', 'website',
            'address', 'description', 'is_active', 'sort_order',
            'seo_title', 'seo_description',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اسلاگ اختیاری - اگر خالی بود، خودکار از روی نام ساخته می‌شود
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data.get('name', ''), allow_unicode=True)
        return slug


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = (
            'manufacturer', 'name', 'slug', 'comb', 'density', 'yarn_type',
            'weight_class', 'description', 'nine_m_waste_type',
            'nine_m_waste_value', 'base_price_12m', 'is_active', 'sort_order',
            'seo_title', 'seo_description',
        )
        widgets = {
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'comb': forms.Select(attrs={'class': 'form-select'}),
            'density': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'yarn_type': forms.Select(attrs={'class': 'form-select'}),
            'weight_class': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nine_m_waste_type': forms.Select(attrs={'class': 'form-select'}),
            'nine_m_waste_value': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'base_price_12m': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manufacturer'].queryset = Manufacturer.objects.filter(is_active=True)
        # اسلاگ اختیاری - اگر خالی بود، خودکار از روی نام ساخته می‌شود
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data.get('name', ''), allow_unicode=True)
        return slug


# ============================================================
# فرم‌های فاز 3: دسته‌بندی‌ها و سایزها
# ============================================================

class BackgroundColorForm(forms.ModelForm):
    class Meta:
        model = BackgroundColor
        fields = ('name', 'slug', 'color_code', 'sort_order', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'color_code': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'width:80px;height:40px;'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class DesignTypeForm(forms.ModelForm):
    class Meta:
        model = DesignType
        fields = ('name', 'slug', 'description', 'sort_order', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class WeaveTypeForm(forms.ModelForm):
    class Meta:
        model = WeaveType
        fields = ('name', 'slug', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ('name', 'slug', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class ColorToneForm(forms.ModelForm):
    class Meta:
        model = ColorTone
        fields = ('name', 'slug', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class CarpetSizeForm(forms.ModelForm):
    class Meta:
        model = CarpetSize
        fields = (
            'name', 'size_type', 'length', 'width', 'diameter',
            'area', 'is_nine_meter', 'default_order_rule',
            'sort_order', 'is_active'
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'size_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_size_type'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'diameter': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.01'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'step': '0.0001', 'readonly': 'readonly'}),
            'default_order_rule': forms.Select(attrs={'class': 'form-select'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }

    def clean(self):
        cleaned = super().clean()
        size_type = cleaned.get('size_type')
        if size_type == CarpetSize.SizeType.ROUND:
            if not cleaned.get('diameter'):
                self.add_error('diameter', 'برای سایز گرد، قطر الزامی است.')
        else:
            if not cleaned.get('length') or not cleaned.get('width'):
                if not cleaned.get('length'):
                    self.add_error('length', 'طول الزامی است.')
                if not cleaned.get('width'):
                    self.add_error('width', 'عرض الزامی است.')
        return cleaned
