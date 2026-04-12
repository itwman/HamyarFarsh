from django.contrib import admin
from .models import HomeSlider, HomeBanner, HomeSection


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'start_date', 'end_date')
    list_editable = ('order', 'is_active')


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'width', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('position',)


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'item_count', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('section_type',)
    filter_horizontal = ('manual_products',)
