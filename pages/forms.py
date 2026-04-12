"""
فرم‌های CMS — ویرایشگر WYSIWYG با Summernote (MIT License — رایگان)
Summernote بدون هیچ لایسنس یا سریال کار می‌کنه و از CDN لود میشه.
"""
from django import forms
from .models import Page, PostCategory


class PageForm(forms.ModelForm):
    """فرم ایجاد/ویرایش صفحه و مقاله"""

    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'page_type', 'category', 'status',
            'content', 'excerpt', 'featured_image',
            'show_in_header', 'show_in_footer', 'menu_order',
            'publish_date', 'seo_title', 'seo_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'autofocus': True,
                'placeholder': 'عنوان صفحه یا مقاله...'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 'dir': 'ltr',
                'placeholder': 'خالی = خودکار از عنوان'
            }),
            'page_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control summernote-editor',
                'id': 'id_content',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'خلاصه برای نمایش در لیست مقالات...'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'show_in_header': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_in_footer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:100px;'}),
            'publish_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 'type': 'datetime-local'
            }),
            'seo_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'خالی = عنوان صفحه'
            }),
            'seo_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'خالی = خلاصه'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = PostCategory.objects.filter(is_active=True)
        self.fields['slug'].required = False


class PostCategoryForm(forms.ModelForm):
    """فرم دسته‌بندی مقالات"""
    class Meta:
        model = PostCategory
        fields = ['name', 'slug', 'description', 'image', 'sort_order', 'is_active',
                  'seo_title', 'seo_description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:100px;'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
