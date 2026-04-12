"""
فاز 14: ویوهای CMS
- پنل مدیریت: لیست/ایجاد/ویرایش صفحات و مقالات
- نمایش عمومی: صفحات ایستا + بلاگ
- SEO: Schema.org + Open Graph
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.utils import timezone
from .models import Page, PostCategory
from .forms import PageForm, PostCategoryForm


from django.contrib.admin.views.decorators import staff_member_required as staff_required


# ===================================================================
#  پنل مدیریت — صفحات و مقالات
# ===================================================================

@staff_required
def page_list(request):
    """لیست صفحات و مقالات"""
    pages = Page.objects.select_related('category', 'author').all()

    # فیلتر نوع
    page_type = request.GET.get('type', '')
    if page_type:
        pages = pages.filter(page_type=page_type)

    # فیلتر وضعیت
    status = request.GET.get('status', '')
    if status:
        pages = pages.filter(status=status)

    # جستجو
    q = request.GET.get('q', '').strip()
    if q:
        pages = pages.filter(Q(title__icontains=q) | Q(content__icontains=q))

    # آمار
    total = Page.objects.count()
    published = Page.objects.filter(status='published').count()
    draft = Page.objects.filter(status='draft').count()
    pages_count = Page.objects.filter(page_type='page').count()
    posts_count = Page.objects.filter(page_type='post').count()

    context = {
        'pages': pages,
        'total': total,
        'published': published,
        'draft': draft,
        'pages_count': pages_count,
        'posts_count': posts_count,
        'current_type': page_type,
        'current_status': status,
        'query': q,
    }
    return render(request, 'pages/admin_list.html', context)


@staff_required
def page_create(request):
    """ایجاد صفحه/مقاله جدید"""
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user
            if page.status == 'published' and not page.publish_date:
                page.publish_date = timezone.now()
            page.save()
            messages.success(request, f'«{page.title}» ایجاد شد.')
            return redirect('pages:page_list')
        else:
            messages.error(request, 'خطا در فرم.')
    else:
        initial = {}
        pt = request.GET.get('type')
        if pt:
            initial['page_type'] = pt
        form = PageForm(initial=initial)

    context = {
        'form': form,
        'title': 'ایجاد محتوای جدید',
        'is_edit': False,
    }
    return render(request, 'pages/admin_form.html', context)


@staff_required
def page_edit(request, pk):
    """ویرایش صفحه/مقاله"""
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            if page.status == 'published' and not page.publish_date:
                page.publish_date = timezone.now()
            page.save()
            messages.success(request, f'«{page.title}» بروزرسانی شد.')
            return redirect('pages:page_list')
        else:
            messages.error(request, 'خطا در فرم.')
    else:
        form = PageForm(instance=page)

    context = {
        'form': form,
        'page_obj': page,
        'title': f'ویرایش: {page.title}',
        'is_edit': True,
    }
    return render(request, 'pages/admin_form.html', context)


@staff_required
def page_delete(request, pk):
    """حذف صفحه"""
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        title = page.title
        page.delete()
        messages.success(request, f'«{title}» حذف شد.')
    return redirect('pages:page_list')


@staff_required
def page_toggle_status(request, pk):
    """تغییر سریع وضعیت"""
    page = get_object_or_404(Page, pk=pk)
    if page.status == 'published':
        page.status = 'draft'
    else:
        page.status = 'published'
        if not page.publish_date:
            page.publish_date = timezone.now()
    page.save(update_fields=['status', 'publish_date'])
    messages.success(request, f'وضعیت «{page.title}» تغییر کرد.')
    return redirect('pages:page_list')


# --- دسته‌بندی مقالات ---
@staff_required
def category_list(request):
    categories = PostCategory.objects.all()
    return render(request, 'pages/admin_categories.html', {'categories': categories})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = PostCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی ایجاد شد.')
            return redirect('pages:category_list')
    else:
        form = PostCategoryForm()
    return render(request, 'pages/admin_category_form.html', {
        'form': form, 'title': 'افزودن دسته‌بندی', 'is_edit': False,
    })


@staff_required
def category_edit(request, pk):
    cat = get_object_or_404(PostCategory, pk=pk)
    if request.method == 'POST':
        form = PostCategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f'«{cat.name}» بروزرسانی شد.')
            return redirect('pages:category_list')
    else:
        form = PostCategoryForm(instance=cat)
    return render(request, 'pages/admin_category_form.html', {
        'form': form, 'category': cat, 'title': f'ویرایش: {cat.name}', 'is_edit': True,
    })


@staff_required
def category_delete(request, pk):
    cat = get_object_or_404(PostCategory, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'دسته‌بندی حذف شد.')
    return redirect('pages:category_list')


# --- آپلود تصویر از ویرایشگر ---
@staff_required
def editor_upload_image(request):
    """آپلود تصویر از ویرایشگر Summernote"""
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        # ذخیره در media/uploads/editor/
        from django.core.files.storage import default_storage
        path = default_storage.save(f'uploads/editor/{f.name}', f)
        url = default_storage.url(path)
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'فایلی ارسال نشد'}, status=400)


# ===================================================================
#  نمایش عمومی — صفحات ایستا
# ===================================================================

def page_view(request, slug):
    """نمایش صفحه ایستا"""
    page = get_object_or_404(Page, slug=slug, status='published', page_type='page')
    Page.objects.filter(pk=page.pk).update(view_count=F('view_count') + 1)

    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page.get_effective_seo_title(),
        "description": page.get_effective_seo_description(),
        "url": request.build_absolute_uri(),
    }
    if page.featured_image:
        schema["image"] = request.build_absolute_uri(page.featured_image.url)

    context = {
        'page': page,
        'schema_json': json.dumps(schema, ensure_ascii=False),
    }
    return render(request, 'pages/page_detail.html', context)


# ===================================================================
#  نمایش عمومی — بلاگ
# ===================================================================

def blog_list(request):
    """لیست مقالات"""
    posts = Page.objects.filter(
        status='published', page_type='post'
    ).select_related('category', 'author').order_by('-publish_date', '-created_at')

    cat_slug = request.GET.get('category')
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)

    q = request.GET.get('q', '').strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(posts, 12)
    page_num = request.GET.get('page')
    posts_page = paginator.get_page(page_num)

    categories = PostCategory.objects.filter(is_active=True)

    context = {
        'posts': posts_page,
        'categories': categories,
        'current_category': cat_slug or '',
        'query': q,
        'total': paginator.count,
    }
    return render(request, 'pages/blog_list.html', context)


def blog_detail(request, slug):
    """نمایش تک مقاله"""
    post = get_object_or_404(Page, slug=slug, status='published', page_type='post')
    Page.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)

    # مقالات مرتبط
    related = Page.objects.filter(
        status='published', page_type='post', category=post.category
    ).exclude(pk=post.pk)[:4] if post.category else Page.objects.none()

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.get_effective_seo_title(),
        "description": post.get_effective_seo_description(),
        "url": request.build_absolute_uri(),
        "datePublished": (post.publish_date or post.created_at).isoformat() if (post.publish_date or post.created_at) else '',
        "dateModified": post.updated_at.isoformat() if post.updated_at else '',
    }
    if post.featured_image:
        schema["image"] = request.build_absolute_uri(post.featured_image.url)
    if post.author:
        schema["author"] = {"@type": "Person", "name": post.author.get_full_name() or 'همیار فرش'}

    context = {
        'post': post,
        'related': related,
        'schema_json': json.dumps(schema, ensure_ascii=False),
    }
    return render(request, 'pages/blog_detail.html', context)


def blog_by_category(request, slug):
    """مقالات بر اساس دسته‌بندی"""
    category = get_object_or_404(PostCategory, slug=slug, is_active=True)
    posts = Page.objects.filter(
        status='published', page_type='post', category=category
    ).order_by('-publish_date')

    paginator = Paginator(posts, 12)
    posts_page = paginator.get_page(request.GET.get('page'))

    categories = PostCategory.objects.filter(is_active=True)

    context = {
        'posts': posts_page,
        'categories': categories,
        'current_category': slug,
        'category': category,
        'total': paginator.count,
    }
    return render(request, 'pages/blog_list.html', context)
