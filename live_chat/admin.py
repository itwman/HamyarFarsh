from django.contrib import admin
from .models import ChatSession, ChatMessage, Ticket, TicketReply


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('message', 'is_admin', 'admin_user', 'created_at')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'visitor_phone', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [ChatMessageInline]


class TicketReplyInline(admin.StackedInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('user', 'message', 'is_admin', 'created_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('pk', 'subject', 'user', 'department', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'department')
    list_editable = ('status',)
    inlines = [TicketReplyInline]
