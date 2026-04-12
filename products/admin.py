from django.contrib import admin
from .models import (
    Product, ProductSizeRule, ProductImage,
    ProductVideo, ProductRating
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('original', 'is_primary', 'alt_text', 'order')


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 0
    fields = ('original_file', 'title', 'order', 'show_in_gallery', 'processing_status')
    readonly_fields = ('processing_status',)


class ProductSizeRuleInline(admin.TabularInline):
    model = ProductSizeRule
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'album', 'background_color', 'status', 'get_sell_price_12m', 'avg_rating', 'created_at')
    list_filter = ('status', 'album__manufacturer', 'album__comb', 'background_color', 'design_type', 'weave_type')
    search_fields = ('name', 'slug', 'album__name', 'album__manufacturer__name')
    list_editable = ('status',)
    filter_horizontal = ('design_type',)
    inlines = [ProductImageInline, ProductVideoInline, ProductSizeRuleInline]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'album', 'status', 'is_featured')
        }),
        ('دسته‌بندی‌ها', {
            'fields': ('background_color', 'design_type', 'weave_type', 'feature', 'color_tone')
        }),
        ('قیمت', {
            'fields': ('purchase_price_12m',),
            'description': 'خالی = استفاده از قیمت آلبوم'
        }),
        ('SEO و محتوا', {
            'fields': ('seo_title', 'seo_description', 'description'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_available', 'make_unavailable']

    @admin.action(description='تغییر وضعیت به موجود')
    def make_available(self, request, queryset):
        updated = queryset.update(status=Product.Status.AVAILABLE)
        self.message_user(request, f'{updated} محصول موجود شد.')

    @admin.action(description='تغییر وضعیت به ناموجود')
    def make_unavailable(self, request, queryset):
        updated = queryset.update(status=Product.Status.UNAVAILABLE)
        self.message_user(request, f'{updated} محصول ناموجود شد.')


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating')
    list_editable = ('status',)
    search_fields = ('product__name', 'user__phone', 'comment')
