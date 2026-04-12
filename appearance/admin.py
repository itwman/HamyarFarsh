from django.contrib import admin
from .models import MenuItem, FooterWidget


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'parent', 'order', 'is_active')
    list_filter = ('position', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(FooterWidget)
class FooterWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'column', 'order', 'is_active')
    list_filter = ('widget_type',)
    list_editable = ('order', 'is_active')
