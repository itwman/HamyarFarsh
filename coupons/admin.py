from django.contrib import admin
from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ('user', 'order', 'discount_amount', 'used_at')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'coupon_type', 'amount', 'max_discount', 'usage_count',
                    'is_active', 'start_date', 'end_date')
    list_filter = ('coupon_type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code', 'description')
    filter_horizontal = ('limited_to_products', 'limited_to_categories')
    inlines = [CouponUsageInline]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'discount_amount', 'used_at')
    list_filter = ('coupon',)
    readonly_fields = ('coupon', 'user', 'order', 'discount_amount', 'used_at')
