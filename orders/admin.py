"""
پنل مدیریت سفارشات
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    """نمایش آیتم‌ها به صورت Inline"""
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('product', 'size', 'quantity', 'unit_price', 'get_total_price', 'is_pair_order')
    
    def get_total_price(self, obj):
        if obj.pk:
            return f"{obj.get_total_price():,} تومان"
        return "-"
    get_total_price.short_description = 'مبلغ کل'


class OrderStatusLogInline(admin.TabularInline):
    """نمایش لاگ‌ها به صورت Inline"""
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'created_at', 'notes')
    fields = ('old_status', 'new_status', 'changed_by', 'created_at', 'notes')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """مدیریت سفارشات"""
    
    list_display = (
        'id', 
        'customer_name', 
        'status_badge', 
        'payment_method_display',
        'total_amount_display',
        'paid_amount_display',
        'remaining_display',
        'created_at_jalali',
    )
    list_filter = ('status', 'payment_method', 'free_shipping', 'is_price_today', 'created_at')
    search_fields = ('id', 'customer__first_name', 'customer__last_name', 'customer__phone')
    readonly_fields = (
        'customer', 
        'created_at', 
        'updated_at',
        'total_amount_display',
        'paid_amount_display',
        'remaining_display',
        'get_items_summary',
    )
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': (
                'customer',
                'status',
                'payment_method',
                'created_at',
                'updated_at',
            )
        }),
        ('مبالغ', {
            'fields': (
                'total_amount_display',
                'deposit_amount',
                'paid_amount_display',
                'remaining_display',
                'shipping_cost',
                'free_shipping',
            )
        }),
        ('آدرس و ارسال', {
            'fields': (
                'shipping_address',
            )
        }),
        ('قیمت روز', {
            'fields': (
                'is_price_today',
                'final_price_at_delivery',
            )
        }),
        ('یادداشت‌ها', {
            'fields': (
                'notes',
                'admin_notes',
            )
        }),
        ('خلاصه آیتم‌ها', {
            'fields': ('get_items_summary',)
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusLogInline]
    
    def customer_name(self, obj):
        return obj.customer.get_full_name()
    customer_name.short_description = 'مشتری'
    
    def status_badge(self, obj):
        """نمایش وضعیت با رنگ"""
        colors = {
            'pending': 'warning',
            'reviewing': 'info',
            'confirmed': 'primary',
            'preparing': 'secondary',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display_persian()
        )
    status_badge.short_description = 'وضعیت'
    
    def payment_method_display(self, obj):
        return obj.get_payment_method_display_persian()
    payment_method_display.short_description = 'روش پرداخت'
    
    def total_amount_display(self, obj):
        return f"{obj.total_amount:,} تومان"
    total_amount_display.short_description = 'مبلغ کل'
    
    def paid_amount_display(self, obj):
        return f"{obj.paid_amount:,} تومان"
    paid_amount_display.short_description = 'پرداخت شده'
    
    def remaining_display(self, obj):
        remaining = obj.get_remaining_amount()
        if remaining > 0:
            # اول عدد را فرمت می‌کنیم، بعد به format_html می‌دهیم
            formatted_amount = f"{remaining:,}"
            return format_html(
                '<span style="color: red; font-weight: bold;">{} تومان</span>',
                formatted_amount
            )
        return format_html('<span style="color: green;">✓ تسویه شده</span>')
    remaining_display.short_description = 'مانده'
    
    def created_at_jalali(self, obj):
        return obj.get_jalali_created_at()
    created_at_jalali.short_description = 'تاریخ ثبت'
    
    def get_items_summary(self, obj):
        """خلاصه آیتم‌های سفارش"""
        if not obj.pk:
            return "-"
        
        items = obj.items.select_related('product', 'size').all()
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f5f5f5;"><th>محصول</th><th>سایز</th><th>تعداد</th><th>قیمت واحد</th><th>جمع</th></tr>'
        
        for item in items:
            size_name = item.size.name if item.size else 'سایز سفارشی'
            html += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td>{item.product.name}</td>
                <td>{size_name}</td>
                <td>{item.quantity}</td>
                <td>{item.unit_price:,} تومان</td>
                <td><strong>{item.get_total_price():,} تومان</strong></td>
            </tr>
            '''
        
        html += '</table>'
        return mark_safe(html)
    get_items_summary.short_description = 'آیتم‌های سفارش'
    
    def has_delete_permission(self, request, obj=None):
        """فقط سفارشات pending قابل حذف هستند"""
        if obj and obj.status != 'pending':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """مدیریت آیتم‌های سفارش"""
    
    list_display = ('id', 'order_id', 'product_name', 'size_name', 'quantity', 'unit_price_display', 'total_display')
    list_filter = ('is_custom_size', 'is_pair_order')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('order', 'product', 'get_total_price')
    
    def order_id(self, obj):
        return f"#{obj.order.id}"
    order_id.short_description = 'شماره سفارش'
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'محصول'
    
    def size_name(self, obj):
        if obj.is_custom_size:
            return f"سفارشی ({obj.custom_length}×{obj.custom_width})"
        return obj.size.name if obj.size else '-'
    size_name.short_description = 'سایز'
    
    def unit_price_display(self, obj):
        return f"{obj.unit_price:,} تومان"
    unit_price_display.short_description = 'قیمت واحد'
    
    def total_display(self, obj):
        return f"{obj.get_total_price():,} تومان"
    total_display.short_description = 'جمع'


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    """مدیریت لاگ‌های وضعیت"""
    
    list_display = ('id', 'order_id', 'old_status', 'new_status', 'changed_by', 'created_at_jalali')
    list_filter = ('old_status', 'new_status', 'created_at')
    search_fields = ('order__id',)
    readonly_fields = ('order', 'old_status', 'new_status', 'changed_by', 'created_at')
    
    def order_id(self, obj):
        return f"#{obj.order.id}"
    order_id.short_description = 'سفارش'
    
    def created_at_jalali(self, obj):
        return obj.get_jalali_created_at()
    created_at_jalali.short_description = 'تاریخ'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
