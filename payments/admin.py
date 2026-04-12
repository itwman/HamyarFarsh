from django.contrib import admin
from .models import PaymentGateway, Transaction, InstallmentPlan, Installment


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'merchant_id', 'is_active', 'is_sandbox']
    list_filter = ['is_active', 'is_sandbox']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'order', 'amount', 'status', 'gateway', 'created_at', 'paid_at']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['tracking_code', 'reference_number', 'authority', 'order__id']
    readonly_fields = ['tracking_code', 'authority', 'reference_number', 'gateway_response', 'created_at', 'paid_at']
    date_hierarchy = 'created_at'


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ['installment_number', 'amount', 'due_date', 'status', 'paid_at']
    can_delete = False


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ['order', 'plan_type', 'num_installments', 'installment_amount', 
                    'is_confirmed', 'created_at']
    list_filter = ['plan_type', 'is_confirmed', 'period', 'created_at']
    search_fields = ['order__id']
    readonly_fields = ['financed_amount', 'total_interest', 'total_with_interest', 
                      'installment_amount', 'created_at', 'confirmed_at']
    inlines = [InstallmentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('اطلاعات اولیه', {
            'fields': ['order', 'plan_type', 'period']
        }),
        ('مبالغ', {
            'fields': ['total_amount', 'down_payment', 'financed_amount', 
                      'interest_rate', 'total_interest', 'total_with_interest']
        }),
        ('اقساط', {
            'fields': ['num_installments', 'installment_amount', 'first_due_date']
        }),
        ('تأیید', {
            'fields': ['is_confirmed', 'confirmed_at', 'confirmed_by']
        }),
    ]


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ['plan', 'installment_number', 'amount', 'due_date', 'status', 'paid_at']
    list_filter = ['status', 'due_date', 'plan__plan_type']
    search_fields = ['plan__order__id', 'check_number']
    date_hierarchy = 'due_date'
