from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import (
    Manufacturer, Album, BackgroundColor, DesignType,
    WeaveType, Feature, ColorTone, CarpetSize
)
from .forms import (
    ManufacturerForm, AlbumForm, BackgroundColorForm, DesignTypeForm,
    WeaveTypeForm, FeatureForm, ColorToneForm, CarpetSizeForm
)


def staff_required(view_func):
    """دکوراتور بررسی دسترسی کارمند/مدیر"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff_user:
            messages.error(request, 'شما دسترسی به این بخش ندارید.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ===========================
# شرکت‌های تولیدی (فاز 2)
# ===========================

@staff_required
def manufacturer_list(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    manufacturers = Manufacturer.objects.annotate(
        album_count=Count('albums'),
        active_albums=Count('albums', filter=Q(albums__is_active=True))
    )
    if query:
        manufacturers = manufacturers.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(mobile__icontains=query)
        )
    if status == 'active':
        manufacturers = manufacturers.filter(is_active=True)
    elif status == 'inactive':
        manufacturers = manufacturers.filter(is_active=False)
    manufacturers = manufacturers.order_by('sort_order', 'name')
    paginator = Paginator(manufacturers, 20)
    page = request.GET.get('page')
    manufacturers = paginator.get_page(page)
    return render(request, 'catalog/manufacturer_list.html', {
        'manufacturers': manufacturers, 'query': query, 'status': status,
    })


@staff_required
def manufacturer_create(request):
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'شرکت تولیدی با موفقیت ایجاد شد.')
            return redirect('manufacturer_list')
    else:
        form = ManufacturerForm()
    return render(request, 'catalog/manufacturer_form.html', {
        'form': form, 'title': 'افزودن شرکت تولیدی', 'is_edit': False,
    })


@staff_required
def manufacturer_edit(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES, instance=manufacturer)
        if form.is_valid():
            form.save()
            messages.success(request, f'شرکت «{manufacturer.name}» بروزرسانی شد.')
            return redirect('manufacturer_list')
    else:
        form = ManufacturerForm(instance=manufacturer)
    return render(request, 'catalog/manufacturer_form.html', {
        'form': form, 'manufacturer': manufacturer,
        'title': f'ویرایش شرکت: {manufacturer.name}', 'is_edit': True,
    })


@staff_required
def manufacturer_delete(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    if request.method == 'POST':
        name = manufacturer.name
        manufacturer.delete()
        messages.success(request, f'شرکت «{name}» حذف شد.')
        return redirect('manufacturer_list')
    return render(request, 'catalog/manufacturer_confirm_delete.html', {
        'manufacturer': manufacturer,
    })


@staff_required
def manufacturer_toggle(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    manufacturer.is_active = not manufacturer.is_active
    manufacturer.save(update_fields=['is_active'])
    status = 'فعال' if manufacturer.is_active else 'غیرفعال'
    messages.success(request, f'شرکت «{manufacturer.name}» {status} شد.')
    return redirect('manufacturer_list')


# ===========================
# آلبوم‌ها (فاز 2)
# ===========================

@staff_required
def album_list(request):
    query = request.GET.get('q', '')
    manufacturer_id = request.GET.get('manufacturer', '')
    comb = request.GET.get('comb', '')
    status = request.GET.get('status', '')
    albums = Album.objects.select_related('manufacturer')
    if query:
        albums = albums.filter(
            Q(name__icontains=query) | Q(manufacturer__name__icontains=query)
        )
    if manufacturer_id:
        albums = albums.filter(manufacturer_id=manufacturer_id)
    if comb:
        albums = albums.filter(comb=comb)
    if status == 'active':
        albums = albums.filter(is_active=True)
    elif status == 'inactive':
        albums = albums.filter(is_active=False)
    albums = albums.order_by('manufacturer__name', 'sort_order', 'name')
    paginator = Paginator(albums, 20)
    page = request.GET.get('page')
    albums = paginator.get_page(page)
    manufacturers = Manufacturer.objects.filter(is_active=True).order_by('name')
    return render(request, 'catalog/album_list.html', {
        'albums': albums, 'manufacturers': manufacturers,
        'query': query, 'selected_manufacturer': manufacturer_id,
        'selected_comb': comb, 'status': status, 'comb_choices': Album.COMB_CHOICES,
    })


@staff_required
def album_create(request):
    manufacturer_id = request.GET.get('manufacturer')
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'آلبوم با موفقیت ایجاد شد.')
            return redirect('album_list')
    else:
        initial = {}
        if manufacturer_id:
            initial['manufacturer'] = manufacturer_id
        form = AlbumForm(initial=initial)
    return render(request, 'catalog/album_form.html', {
        'form': form, 'title': 'افزودن آلبوم', 'is_edit': False,
    })


@staff_required
def album_edit(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, f'آلبوم «{album.name}» بروزرسانی شد.')
            return redirect('album_list')
    else:
        form = AlbumForm(instance=album)
    return render(request, 'catalog/album_form.html', {
        'form': form, 'album': album,
        'title': f'ویرایش آلبوم: {album.name}', 'is_edit': True,
    })


@staff_required
def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.method == 'POST':
        name = album.name
        album.delete()
        messages.success(request, f'آلبوم «{name}» حذف شد.')
        return redirect('album_list')
    return render(request, 'catalog/album_confirm_delete.html', {'album': album})


@staff_required
def album_toggle(request, pk):
    album = get_object_or_404(Album, pk=pk)
    album.is_active = not album.is_active
    album.save(update_fields=['is_active'])
    status = 'فعال' if album.is_active else 'غیرفعال'
    messages.success(request, f'آلبوم «{album.name}» {status} شد.')
    return redirect('album_list')


# ===========================
# فاز 3: ویو عمومی دسته‌بندی‌ها
# ===========================

@staff_required
def categories_dashboard(request):
    """داشبورد مدیریت دسته‌بندی‌ها و سایزها"""
    context = {
        'colors': BackgroundColor.objects.all(),
        'designs': DesignType.objects.all(),
        'weaves': WeaveType.objects.all(),
        'features': Feature.objects.all(),
        'tones': ColorTone.objects.all(),
        'sizes': CarpetSize.objects.all(),
        'color_count': BackgroundColor.objects.count(),
        'design_count': DesignType.objects.count(),
        'weave_count': WeaveType.objects.count(),
        'feature_count': Feature.objects.count(),
        'tone_count': ColorTone.objects.count(),
        'size_count': CarpetSize.objects.count(),
    }
    return render(request, 'catalog/categories_dashboard.html', context)


# --- Generic CRUD helper for simple category models ---

def _category_crud(request, model_class, form_class, template_prefix,
                   list_name, verbose_name, pk=None, action='list'):
    """ویوی عمومی CRUD برای دسته‌بندی‌های ساده"""

    if action == 'list':
        items = model_class.objects.all()
        query = request.GET.get('q', '')
        if query:
            items = items.filter(name__icontains=query)
        return render(request, f'catalog/{template_prefix}_list.html', {
            'items': items, 'query': query, 'verbose_name': verbose_name,
        })

    elif action == 'create':
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'{verbose_name} با موفقیت ایجاد شد.')
                return redirect(list_name)
        else:
            form = form_class()
        return render(request, f'catalog/{template_prefix}_form.html', {
            'form': form, 'title': f'افزودن {verbose_name}', 'is_edit': False,
            'list_url_name': list_name, 'verbose_name': verbose_name,
        })

    elif action == 'edit':
        obj = get_object_or_404(model_class, pk=pk)
        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, f'{verbose_name} «{obj.name}» بروزرسانی شد.')
                return redirect(list_name)
        else:
            form = form_class(instance=obj)
        return render(request, f'catalog/{template_prefix}_form.html', {
            'form': form, 'obj': obj, 'title': f'ویرایش {verbose_name}: {obj.name}',
            'is_edit': True, 'list_url_name': list_name, 'verbose_name': verbose_name,
        })

    elif action == 'delete':
        obj = get_object_or_404(model_class, pk=pk)
        if request.method == 'POST':
            name = obj.name
            obj.delete()
            messages.success(request, f'{verbose_name} «{name}» حذف شد.')
            return redirect(list_name)
        return render(request, 'catalog/category_confirm_delete.html', {
            'obj': obj, 'verbose_name': verbose_name, 'list_url_name': list_name,
        })

    elif action == 'toggle':
        obj = get_object_or_404(model_class, pk=pk)
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        status = 'فعال' if obj.is_active else 'غیرفعال'
        messages.success(request, f'{verbose_name} «{obj.name}» {status} شد.')
        return redirect(list_name)


# --- رنگ زمینه ---
@staff_required
def color_list(request):
    return _category_crud(request, BackgroundColor, BackgroundColorForm,
                          'category', 'color_list', 'رنگ زمینه', action='list')

@staff_required
def color_create(request):
    return _category_crud(request, BackgroundColor, BackgroundColorForm,
                          'category', 'color_list', 'رنگ زمینه', action='create')

@staff_required
def color_edit(request, pk):
    return _category_crud(request, BackgroundColor, BackgroundColorForm,
                          'category', 'color_list', 'رنگ زمینه', pk=pk, action='edit')

@staff_required
def color_delete(request, pk):
    return _category_crud(request, BackgroundColor, BackgroundColorForm,
                          'category', 'color_list', 'رنگ زمینه', pk=pk, action='delete')

@staff_required
def color_toggle(request, pk):
    return _category_crud(request, BackgroundColor, BackgroundColorForm,
                          'category', 'color_list', 'رنگ زمینه', pk=pk, action='toggle')


# --- نوع طرح ---
@staff_required
def design_list(request):
    return _category_crud(request, DesignType, DesignTypeForm,
                          'category', 'design_list', 'نوع طرح', action='list')

@staff_required
def design_create(request):
    return _category_crud(request, DesignType, DesignTypeForm,
                          'category', 'design_list', 'نوع طرح', action='create')

@staff_required
def design_edit(request, pk):
    return _category_crud(request, DesignType, DesignTypeForm,
                          'category', 'design_list', 'نوع طرح', pk=pk, action='edit')

@staff_required
def design_delete(request, pk):
    return _category_crud(request, DesignType, DesignTypeForm,
                          'category', 'design_list', 'نوع طرح', pk=pk, action='delete')

@staff_required
def design_toggle(request, pk):
    return _category_crud(request, DesignType, DesignTypeForm,
                          'category', 'design_list', 'نوع طرح', pk=pk, action='toggle')


# --- نوع بافت ---
@staff_required
def weave_list(request):
    return _category_crud(request, WeaveType, WeaveTypeForm,
                          'category', 'weave_list', 'نوع بافت', action='list')

@staff_required
def weave_create(request):
    return _category_crud(request, WeaveType, WeaveTypeForm,
                          'category', 'weave_list', 'نوع بافت', action='create')

@staff_required
def weave_edit(request, pk):
    return _category_crud(request, WeaveType, WeaveTypeForm,
                          'category', 'weave_list', 'نوع بافت', pk=pk, action='edit')

@staff_required
def weave_delete(request, pk):
    return _category_crud(request, WeaveType, WeaveTypeForm,
                          'category', 'weave_list', 'نوع بافت', pk=pk, action='delete')


# --- ویژگی ---
@staff_required
def feature_list(request):
    return _category_crud(request, Feature, FeatureForm,
                          'category', 'feature_list', 'ویژگی', action='list')

@staff_required
def feature_create(request):
    return _category_crud(request, Feature, FeatureForm,
                          'category', 'feature_list', 'ویژگی', action='create')

@staff_required
def feature_edit(request, pk):
    return _category_crud(request, Feature, FeatureForm,
                          'category', 'feature_list', 'ویژگی', pk=pk, action='edit')

@staff_required
def feature_delete(request, pk):
    return _category_crud(request, Feature, FeatureForm,
                          'category', 'feature_list', 'ویژگی', pk=pk, action='delete')


# --- تناژ رنگ ---
@staff_required
def tone_list(request):
    return _category_crud(request, ColorTone, ColorToneForm,
                          'category', 'tone_list', 'تناژ رنگ', action='list')

@staff_required
def tone_create(request):
    return _category_crud(request, ColorTone, ColorToneForm,
                          'category', 'tone_list', 'تناژ رنگ', action='create')

@staff_required
def tone_edit(request, pk):
    return _category_crud(request, ColorTone, ColorToneForm,
                          'category', 'tone_list', 'تناژ رنگ', pk=pk, action='edit')

@staff_required
def tone_delete(request, pk):
    return _category_crud(request, ColorTone, ColorToneForm,
                          'category', 'tone_list', 'تناژ رنگ', pk=pk, action='delete')


# --- سایزهای فرش ---
@staff_required
def size_list(request):
    sizes = CarpetSize.objects.all()
    size_type = request.GET.get('type', '')
    if size_type:
        sizes = sizes.filter(size_type=size_type)
    return render(request, 'catalog/size_list.html', {
        'sizes': sizes, 'size_type': size_type,
        'size_type_choices': CarpetSize.SizeType.choices,
    })

@staff_required
def size_create(request):
    if request.method == 'POST':
        form = CarpetSizeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'سایز جدید با موفقیت ایجاد شد.')
            return redirect('size_list')
    else:
        form = CarpetSizeForm()
    return render(request, 'catalog/size_form.html', {
        'form': form, 'title': 'افزودن سایز', 'is_edit': False,
    })

@staff_required
def size_edit(request, pk):
    size = get_object_or_404(CarpetSize, pk=pk)
    if request.method == 'POST':
        form = CarpetSizeForm(request.POST, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, f'سایز «{size.name}» بروزرسانی شد.')
            return redirect('size_list')
    else:
        form = CarpetSizeForm(instance=size)
    return render(request, 'catalog/size_form.html', {
        'form': form, 'size': size, 'title': f'ویرایش سایز: {size.name}', 'is_edit': True,
    })

@staff_required
def size_delete(request, pk):
    size = get_object_or_404(CarpetSize, pk=pk)
    if request.method == 'POST':
        name = size.name
        size.delete()
        messages.success(request, f'سایز «{name}» حذف شد.')
        return redirect('size_list')
    return render(request, 'catalog/size_confirm_delete.html', {'size': size})

@staff_required
def size_toggle(request, pk):
    size = get_object_or_404(CarpetSize, pk=pk)
    size.is_active = not size.is_active
    size.save(update_fields=['is_active'])
    status = 'فعال' if size.is_active else 'غیرفعال'
    messages.success(request, f'سایز «{size.name}» {status} شد.')
    return redirect('size_list')
