from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات سایت', {'fields': ('site_name', 'logo', 'favicon')}),
        ('اطلاعات تماس', {'fields': ('phone', 'mobile', 'whatsapp', 'telegram_id', 'instagram_id', 'eitaa_id', 'bale_id', 'website_url', 'address')}),
        ('تنظیمات تصویر', {'fields': ('thumbnail_width', 'thumbnail_height', 'featured_image_size', 'info_bar_color')}),
        ('تنظیمات قیمت‌گذاری', {'fields': ('profit_percent', 'shipping_cost', 'rounding_step')}),
        ('تنظیمات سفارش', {'fields': ('free_shipping_min', 'deposit_percent', 'cancellation_fee_percent')}),
        ('تنظیمات اقساط', {'fields': ('installment_max', 'check_max_months', 'check_monthly_rate', 'check_bimonthly_rate', 'check_prepay_required', 'beta_max_months', 'beta_monthly_rate', 'beta_prepay_required')}),
        ('تنظیمات SEO', {'fields': ('seo_title', 'seo_description', 'seo_keywords', 'product_desc_template'), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
