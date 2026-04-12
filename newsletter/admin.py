from django.contrib import admin
from .models import NewsletterSubscriber, SMSCampaign, CampaignLog


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'status', 'source', 'subscribed_at')
    list_filter = ('status', 'source')
    search_fields = ('phone', 'name')
    list_editable = ('status',)


class CampaignLogInline(admin.TabularInline):
    model = CampaignLog
    extra = 0
    readonly_fields = ('phone', 'status', 'sent_at')


@admin.register(SMSCampaign)
class SMSCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'total_recipients', 'sent_count', 'failed_count', 'created_at')
    list_filter = ('status',)
    inlines = [CampaignLogInline]
