from django.contrib import admin
from .models import Page, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'status', 'category', 'view_count', 'created_at')
    list_filter = ('page_type', 'status', 'category')
    search_fields = ('title', 'content')
    list_editable = ('status',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'page_type', 'category', 'status', 'author')
        }),
        ('محتوا', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('فهرست', {
            'fields': ('show_in_header', 'show_in_footer', 'menu_order')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
    )
