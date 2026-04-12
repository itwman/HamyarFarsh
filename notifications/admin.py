from django.contrib import admin
from .models import Announcement, Notification, SMSTemplate, SMSLog


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'start_date', 'end_date', 'order')
    list_editable = ('is_active', 'order')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notif_type', 'is_read', 'created_at')
    list_filter = ('notif_type', 'is_read')


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('event', 'is_active')
    list_editable = ('is_active',)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('phone', 'event', 'status', 'sent_at')
    list_filter = ('status', 'event')
    readonly_fields = ('phone', 'message', 'event', 'status', 'api_response', 'sent_at')
