from django.contrib import admin
from .models import (
    Manufacturer, Album, BackgroundColor, DesignType,
    WeaveType, Feature, ColorTone, CarpetSize
)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_active', 'get_album_count', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'phone', 'mobile')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'sort_order')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'comb', 'yarn_type', 'weight_class',
                    'nine_m_waste_type', 'base_price_12m', 'is_active')
    list_filter = ('manufacturer', 'comb', 'yarn_type', 'weight_class', 'is_active')
    search_fields = ('name', 'manufacturer__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


@admin.register(BackgroundColor)
class BackgroundColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active', 'color_code')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(DesignType)
class DesignTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(WeaveType)
class WeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ColorTone)
class ColorToneAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CarpetSize)
class CarpetSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'size_type', 'dimensions_display', 'area_display',
                    'default_order_rule', 'is_nine_meter', 'sort_order', 'is_active')
    list_filter = ('size_type', 'default_order_rule', 'is_nine_meter', 'is_active')
    list_editable = ('sort_order', 'is_active', 'default_order_rule')
    search_fields = ('name',)
