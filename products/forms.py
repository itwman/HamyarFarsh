from django import forms
from .models import Product, ProductImage, ProductVideo, ProductSizeRule
from catalog.models import Album, Manufacturer


class MultiFileInput(forms.ClearableFileInput):
    """ویجت آپلود چند فایل - سازگار با Django 5"""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        super().__init__(attrs=attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class ProductForm(forms.ModelForm):
    """فرم افزودن/ویرایش محصول - با Select2 Autocomplete"""

    manufacturer_filter = forms.ModelChoiceField(
        queryset=Manufacturer.objects.filter(is_active=True),
        required=False, label='فیلتر شرکت',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'filterAlbums(this.value)',
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'album', 'background_color', 'design_type',
            'weave_type', 'feature', 'color_tone',
            'purchase_price_12m', 'status', 'is_featured',
            'seo_title', 'seo_description', 'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'album': forms.Select(attrs={'class': 'form-select select2-single'}),
            'background_color': forms.Select(attrs={'class': 'form-select select2-single', 'data-placeholder': 'انتخاب رنگ...'}),
            'design_type': forms.SelectMultiple(attrs={'class': 'form-select select2-multi', 'data-placeholder': 'انتخاب طرح‌ها... (چندتایی)'}),
            'weave_type': forms.Select(attrs={'class': 'form-select select2-single', 'data-placeholder': 'انتخاب بافت...'}),
            'feature': forms.Select(attrs={'class': 'form-select select2-single', 'data-placeholder': 'انتخاب ویژگی...'}),
            'color_tone': forms.Select(attrs={'class': 'form-select select2-single', 'data-placeholder': 'انتخاب تناژ...'}),
            'purchase_price_12m': forms.NumberInput(attrs={
                'class': 'form-control', 'dir': 'ltr',
                'placeholder': 'خالی = قیمت آلبوم'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تنظیم queryset برای آلبوم‌ها
        albums = Album.objects.filter(is_active=True).select_related('manufacturer').order_by('manufacturer__name', 'name')
        self.fields['album'].queryset = albums
        
        # تنظیم label برای هر آلبوم
        self.fields['album'].label_from_instance = lambda obj: f"{obj.manufacturer.name} - {obj.name}"
        
        # اضافه کردن data-manufacturer به هر option
        # این کار را بعد از render انجام می‌دهیم با یک متد کمکی
        self.fields['album'].widget.attrs['data-albums'] = {}
        for album in albums:
            self.fields['album'].widget.attrs['data-albums'][str(album.id)] = str(album.manufacturer.id)


class ProductImageForm(forms.ModelForm):
    """فرم آپلود تصویر"""
    class Meta:
        model = ProductImage
        fields = ['original', 'is_primary', 'alt_text', 'order']
        widgets = {
            'original': forms.FileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class MultiImageUploadForm(forms.Form):
    """فرم آپلود چند تصویر همزمان"""
    images = forms.FileField(
        widget=MultiFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        label='انتخاب تصاویر',
        required=True,
    )


class ProductFilterForm(forms.Form):
    """فرم فیلتر محصولات"""
    search = forms.CharField(
        required=False, label='جستجو',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'نام نقشه...'
        })
    )
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.filter(is_active=True),
        required=False, label='شرکت',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    album = forms.ModelChoiceField(
        queryset=Album.objects.filter(is_active=True),
        required=False, label='آلبوم',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comb = forms.ChoiceField(
        required=False, label='شانه',
        choices=[('', 'همه')] + Album.COMB_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False, label='وضعیت',
        choices=[('', 'همه')] + list(Product.Status.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    background_color = forms.ModelChoiceField(
        queryset=None, required=False, label='رنگ زمینه',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    design_type = forms.ModelChoiceField(
        queryset=None, required=False, label='نوع طرح',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from catalog.models import BackgroundColor, DesignType
        self.fields['background_color'].queryset = BackgroundColor.objects.filter(is_active=True)
        self.fields['design_type'].queryset = DesignType.objects.filter(is_active=True)


class ProductVideoForm(forms.ModelForm):
    """فرم آپلود ویدیو"""
    class Meta:
        model = ProductVideo
        fields = ['original_file', 'title', 'description', 'order', 'is_featured', 'show_in_gallery']
        widgets = {
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/avi,video/mkv,video/mov,video/webm,video/*',
            }),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'خالی = تولید خودکار'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'dir': 'ltr', 'value': '0'}),
        }
