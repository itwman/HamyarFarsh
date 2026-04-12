"""
فاز 15: ویوهای مدیریت صفحه اصلی + رندر صفحه اصلی پویا
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import HomeSlider, HomeBanner, HomeSection
from .forms import HomeSliderForm, HomeBannerForm, HomeSectionForm


# ===================================================================
#  صفحه اصلی پویا
# ===================================================================

def home_view(request):
    """صفحه اصلی — رندر پویا بر اساس اسلایدر + بنر + بخش‌ها"""
    sliders = [s for s in HomeSlider.objects.filter(is_active=True).order_by('order') if s.is_visible]
    banners_top = [b for b in HomeBanner.objects.filter(is_active=True, position='top').order_by('order') if b.is_visible]
    banners_middle = [b for b in HomeBanner.objects.filter(is_active=True, position='middle').order_by('order') if b.is_visible]
    banners_bottom = [b for b in HomeBanner.objects.filter(is_active=True, position='bottom').order_by('order') if b.is_visible]
    sections = HomeSection.objects.filter(is_active=True).order_by('order')

    context = {
        'sliders': sliders,
        'banners_top': banners_top,
        'banners_middle': banners_middle,
        'banners_bottom': banners_bottom,
        'sections': sections,
    }
    return render(request, 'home.html', context)


# ===================================================================
#  داشبورد مدیریت صفحه اصلی
# ===================================================================

@staff_member_required
def dashboard_home(request):
    """داشبورد مدیریت صفحه اصلی"""
    context = {
        'sliders': HomeSlider.objects.all().order_by('order'),
        'banners': HomeBanner.objects.all().order_by('position', 'order'),
        'sections': HomeSection.objects.all().order_by('order'),
    }
    return render(request, 'home_manager/dashboard.html', context)


# --- اسلایدر ---
@staff_member_required
def slider_create(request):
    if request.method == 'POST':
        form = HomeSliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'اسلاید جدید اضافه شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeSliderForm()
    return render(request, 'home_manager/slider_form.html', {'form': form, 'title': 'افزودن اسلاید', 'is_edit': False})


@staff_member_required
def slider_edit(request, pk):
    slider = get_object_or_404(HomeSlider, pk=pk)
    if request.method == 'POST':
        form = HomeSliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            messages.success(request, f'اسلاید «{slider.title}» بروزرسانی شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeSliderForm(instance=slider)
    return render(request, 'home_manager/slider_form.html', {'form': form, 'slider': slider, 'title': f'ویرایش: {slider.title}', 'is_edit': True})


@staff_member_required
def slider_delete(request, pk):
    slider = get_object_or_404(HomeSlider, pk=pk)
    if request.method == 'POST':
        slider.delete()
        messages.success(request, 'اسلاید حذف شد.')
    return redirect('home_manager:dashboard')


# --- بنر ---
@staff_member_required
def banner_create(request):
    if request.method == 'POST':
        form = HomeBannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'بنر اضافه شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeBannerForm()
    return render(request, 'home_manager/banner_form.html', {'form': form, 'title': 'افزودن بنر', 'is_edit': False})


@staff_member_required
def banner_edit(request, pk):
    banner = get_object_or_404(HomeBanner, pk=pk)
    if request.method == 'POST':
        form = HomeBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, f'بنر «{banner.title}» بروزرسانی شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeBannerForm(instance=banner)
    return render(request, 'home_manager/banner_form.html', {'form': form, 'banner': banner, 'title': f'ویرایش: {banner.title}', 'is_edit': True})


@staff_member_required
def banner_delete(request, pk):
    banner = get_object_or_404(HomeBanner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'بنر حذف شد.')
    return redirect('home_manager:dashboard')


# --- بخش سفارشی ---
@staff_member_required
def section_create(request):
    if request.method == 'POST':
        form = HomeSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'بخش اضافه شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeSectionForm()
    return render(request, 'home_manager/section_form.html', {'form': form, 'title': 'افزودن بخش', 'is_edit': False})


@staff_member_required
def section_edit(request, pk):
    section = get_object_or_404(HomeSection, pk=pk)
    if request.method == 'POST':
        form = HomeSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f'بخش «{section.title}» بروزرسانی شد.')
            return redirect('home_manager:dashboard')
    else:
        form = HomeSectionForm(instance=section)
    return render(request, 'home_manager/section_form.html', {'form': form, 'section': section, 'title': f'ویرایش: {section.title}', 'is_edit': True})


@staff_member_required
def section_delete(request, pk):
    section = get_object_or_404(HomeSection, pk=pk)
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'بخش حذف شد.')
    return redirect('home_manager:dashboard')
