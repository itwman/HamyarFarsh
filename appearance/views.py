"""
فاز 16: ویوهای مدیریت ظاهر سایت
- فهرست‌ها (MenuItem)
- ویجت فوتر (FooterWidget)
- کد سفارشی و رنگ‌بندی (SiteSettings)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import MenuItem, FooterWidget
from .forms import MenuItemForm, FooterWidgetForm
from settings_app.models import SiteSettings


# ===================================================================
#  داشبورد ظاهر سایت
# ===================================================================

@staff_member_required
def appearance_dashboard(request):
    """داشبورد مدیریت ظاهر سایت"""
    header_items = MenuItem.objects.filter(
        position__in=['header', 'both'], parent__isnull=True
    ).prefetch_related('children').order_by('order')
    footer_items = MenuItem.objects.filter(
        position__in=['footer', 'both'], parent__isnull=True
    ).prefetch_related('children').order_by('order')
    widgets = FooterWidget.objects.all().order_by('column', 'order')
    ss = SiteSettings.get_solo()

    context = {
        'header_items': header_items,
        'footer_items': footer_items,
        'widgets': widgets,
        'ss': ss,
    }
    return render(request, 'appearance/dashboard.html', context)


# --- آیتم فهرست ---
@staff_member_required
def menu_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'آیتم فهرست اضافه شد.')
            return redirect('appearance:dashboard')
    else:
        initial = {}
        pos = request.GET.get('position')
        if pos:
            initial['position'] = pos
        form = MenuItemForm(initial=initial)
    return render(request, 'appearance/menu_form.html', {
        'form': form, 'title': 'افزودن آیتم فهرست', 'is_edit': False
    })


@staff_member_required
def menu_edit(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'«{item.title}» بروزرسانی شد.')
            return redirect('appearance:dashboard')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'appearance/menu_form.html', {
        'form': form, 'item': item, 'title': f'ویرایش: {item.title}', 'is_edit': True
    })


@staff_member_required
def menu_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'آیتم حذف شد.')
    return redirect('appearance:dashboard')


# --- ویجت فوتر ---
@staff_member_required
def widget_create(request):
    if request.method == 'POST':
        form = FooterWidgetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ویجت اضافه شد.')
            return redirect('appearance:dashboard')
    else:
        form = FooterWidgetForm()
    return render(request, 'appearance/widget_form.html', {
        'form': form, 'title': 'افزودن ویجت فوتر', 'is_edit': False
    })


@staff_member_required
def widget_edit(request, pk):
    widget = get_object_or_404(FooterWidget, pk=pk)
    if request.method == 'POST':
        form = FooterWidgetForm(request.POST, instance=widget)
        if form.is_valid():
            form.save()
            messages.success(request, f'ویجت «{widget.title}» بروزرسانی شد.')
            return redirect('appearance:dashboard')
    else:
        form = FooterWidgetForm(instance=widget)
    return render(request, 'appearance/widget_form.html', {
        'form': form, 'widget': widget, 'title': f'ویرایش: {widget.title}', 'is_edit': True
    })


@staff_member_required
def widget_delete(request, pk):
    widget = get_object_or_404(FooterWidget, pk=pk)
    if request.method == 'POST':
        widget.delete()
        messages.success(request, 'ویجت حذف شد.')
    return redirect('appearance:dashboard')


# --- کد سفارشی و رنگ‌بندی ---
@staff_member_required
def custom_code_settings(request):
    """تنظیمات کد سفارشی Head/Body/Footer + رنگ‌بندی"""
    ss = SiteSettings.get_solo()
    if request.method == 'POST':
        ss.custom_head_code = request.POST.get('custom_head_code', '')
        ss.custom_body_start = request.POST.get('custom_body_start', '')
        ss.custom_body_end = request.POST.get('custom_body_end', '')
        ss.custom_footer_code = request.POST.get('custom_footer_code', '')
        ss.primary_color = request.POST.get('primary_color', '#C62828')
        ss.secondary_color = request.POST.get('secondary_color', '#1565C0')
        ss.header_bg_color = request.POST.get('header_bg_color', '#FFFFFF')
        ss.footer_bg_color = request.POST.get('footer_bg_color', '#212121')
        ss.save()
        messages.success(request, 'تنظیمات ظاهری ذخیره شد.')
        return redirect('appearance:dashboard')

    return render(request, 'appearance/custom_code.html', {'ss': ss})
