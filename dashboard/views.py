"""
ویوهای داشبورد مدیریت
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from accounts.models import User
from orders.models import Order, OrderItem, OrderStatusLog
from products.models import Product
from products.models import ProductRating
from settings_app.models import SiteSettings
from accounts.forms import AdminUserCreateForm, AdminUserEditForm, AdminPasswordResetForm


@login_required
def dashboard_home(request):
    """صفحه اصلی داشبورد"""
    if not request.user.is_staff_user:
        messages.error(request, 'شما دسترسی به داشبورد ندارید.')
        return redirect('home')
    
    # محاسبات آماری
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # آمار کلی
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    pending_orders = Order.objects.filter(status='pending').count()
    total_customers = User.objects.filter(role='customer').count()
    total_products = Product.objects.filter(status='available').count()
    
    # آمار 30 روز اخیر
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago)
    recent_revenue = recent_orders.filter(status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    recent_orders_count = recent_orders.count()
    
    # آمار روزانه (7 روز اخیر)
    seven_days_ago = today - timedelta(days=7)
    daily_stats = Order.objects.filter(
        created_at__gte=seven_days_ago,
        created_at__isnull=False  # ✅ فیلتر کردن Null ها
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('date')
    
    # تبدیل به لیست برای Chart.js - با بررسی None
    daily_labels = []
    daily_orders = []
    daily_revenue_data = []
    
    for stat in daily_stats:
        if stat['date']:  # ✅ بررسی None
            daily_labels.append(stat['date'].strftime('%Y-%m-%d'))
            daily_orders.append(stat['count'])
            daily_revenue_data.append(float(stat['revenue'] or 0))
    
    # آخرین سفارشات
    latest_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
    
    # محصولات پرفروش
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('unit_price')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'recent_orders_count': recent_orders_count,
        'recent_revenue': recent_revenue,
        'latest_orders': latest_orders,
        'top_products': top_products,
        'daily_labels': daily_labels,
        'daily_orders': daily_orders,
        'daily_revenue': daily_revenue_data,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def users_list(request):
    """لیست کاربران"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('dashboard:home')
    
    users = User.objects.all().order_by('-date_joined')
    
    # فیلتر نقش
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    # جستجو
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(phone__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'roles': User.Role.choices,
    }
    
    return render(request, 'dashboard/users_list.html', context)


@login_required
def user_create(request):
    """افزودن کاربر جدید توسط مدیر"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'کاربر «{user.get_full_name() or user.phone}» با موفقیت افزوده شد.')
            return redirect('dashboard:users_list')
    else:
        form = AdminUserCreateForm()

    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'mode': 'create',
        'page_title': 'افزودن کاربر جدید',
    })


@login_required
def user_edit(request, user_id):
    """ویرایش کاربر توسط مدیر"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('dashboard:home')

    target = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, f'تغییرات کاربر «{target.get_full_name() or target.phone}» ذخیره شد.')
            return redirect('dashboard:users_list')
    else:
        form = AdminUserEditForm(instance=target)

    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'mode': 'edit',
        'target_user': target,
        'page_title': f'ویرایش کاربر: {target.get_full_name() or target.phone}',
    })


@login_required
def user_password_reset(request, user_id):
    """تغییر رمز کاربر توسط مدیر"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('dashboard:home')

    target = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            target.set_password(form.cleaned_data['new_password1'])
            target.save()
            messages.success(request, f'رمز عبور کاربر «{target.get_full_name() or target.phone}» تغییر کرد.')
            return redirect('dashboard:users_list')
    else:
        form = AdminPasswordResetForm()

    return render(request, 'dashboard/user_password_reset.html', {
        'form': form,
        'target_user': target,
    })


@login_required
def user_toggle_active(request, user_id):
    """فعال/غیرفعال کردن کاربر (POST)"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('dashboard:home')

    target = get_object_or_404(User, pk=user_id)

    # محافظت: خود کاربر نمی‌تونه خودش رو غیرفعال کنه
    if target.pk == request.user.pk:
        messages.error(request, 'نمی‌توانید حساب خودتان را غیرفعال کنید.')
        return redirect('dashboard:users_list')

    if request.method == 'POST':
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        status = 'فعال' if target.is_active else 'غیرفعال'
        messages.success(request, f'کاربر «{target.get_full_name() or target.phone}» {status} شد.')

    return redirect('dashboard:users_list')


@login_required
def user_delete(request, user_id):
    """حذف کاربر (فقط توسط superuser جلوگیری می‌شود از حذف کاربر دارای داده)"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('dashboard:home')

    target = get_object_or_404(User, pk=user_id)

    # جلوگیری از حذف خود کاربر
    if target.pk == request.user.pk:
        messages.error(request, 'نمی‌توانید حساب خودتان را حذف کنید.')
        return redirect('dashboard:users_list')

    # بررسی وابستگی‌ها (سفارشات, نظرات, ...)
    has_orders = Order.objects.filter(customer=target).exists()

    if request.method == 'POST':
        if has_orders:
            # به جای حذف، غیرفعال کن
            target.is_active = False
            target.save(update_fields=['is_active'])
            messages.warning(request, f'کاربر «{target.phone}» دارای سفارش بود، به جای حذف غیرفعال شد.')
        else:
            phone = target.phone
            target.delete()
            messages.success(request, f'کاربر «{phone}» حذف شد.')
        return redirect('dashboard:users_list')

    return render(request, 'dashboard/user_confirm_delete.html', {
        'target_user': target,
        'has_orders': has_orders,
    })


@login_required
def sms_settings(request):
    """تنظیمات پیامک"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('dashboard:home')
    
    site_settings = SiteSettings.get_solo()
    
    if request.method == 'POST':
        # دریافت داده‌ها از فرم
        site_settings.sms_api_key = request.POST.get('sms_api_key', '')
        site_settings.sms_sender = request.POST.get('sms_sender', '')
        site_settings.sms_enabled = request.POST.get('sms_enabled') == 'on'
        site_settings.sms_on_order = request.POST.get('sms_on_order') == 'on'
        site_settings.sms_on_confirm = request.POST.get('sms_on_confirm') == 'on'
        site_settings.sms_on_shipped = request.POST.get('sms_on_shipped') == 'on'
        site_settings.sms_on_delivered = request.POST.get('sms_on_delivered') == 'on'
        
        # ذخیره
        site_settings.save()
        
        messages.success(request, 'تنظیمات پیامک با موفقیت ذخیره شد.')
        return redirect('dashboard:sms_settings')
    
    context = {
        'site_settings': site_settings,
    }
    
    return render(request, 'dashboard/sms_settings.html', context)


@login_required
def sms_test_connection(request):
    """تست اتصال به سرویس پیامک (AJAX)"""
    if not request.user.is_admin_user:
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'}, status=403)
    
    try:
        from utils.sms import get_sms_credit
        result = get_sms_credit()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'خطا: {str(e)}'})


@login_required
def reports(request):
    """گزارشات فروش"""
    if not request.user.is_staff_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('dashboard:home')
    
    # دریافت بازه زمانی
    period = request.GET.get('period', '30days')
    
    today = timezone.now().date()
    
    if period == '7days':
        start_date = today - timedelta(days=7)
    elif period == '30days':
        start_date = today - timedelta(days=30)
    elif period == '90days':
        start_date = today - timedelta(days=90)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)
    
    # آمار کلی دوره
    period_orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__isnull=False  # ✅ فیلتر کردن Null ها
    )
    
    stats = {
        'total_orders': period_orders.count(),
        'completed_orders': period_orders.filter(status='completed').count(),
        'cancelled_orders': period_orders.filter(status='cancelled').count(),
        'total_revenue': period_orders.filter(status='completed').aggregate(
            total=Sum('total_amount'))['total'] or 0,
        'avg_order_value': period_orders.filter(status='completed').aggregate(
            avg=Avg('total_amount'))['avg'] or 0,
    }
    
    # نمودار روند فروش
    if period in ['7days', '30days']:
        trend = period_orders.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('date')
        
        labels = [t['date'].strftime('%Y-%m-%d') for t in trend if t['date']]
    else:
        trend = period_orders.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('month')
        
        labels = [t['month'].strftime('%Y-%m') for t in trend if t['month']]
    
    orders_data = [t['count'] for t in trend]
    revenue_data = [float(t['revenue'] or 0) for t in trend]
    
    context = {
        'period': period,
        'stats': stats,
        'labels': labels,
        'orders_data': orders_data,
        'revenue_data': revenue_data,
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def orders_manage(request):
    """مدیریت سفارشات - فقط برای staff"""
    if not request.user.is_staff_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('home')
    
    # دریافت تمام سفارشات با اطلاعات مرتبط
    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    
    # فیلتر وضعیت
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # جستجو (ID، شماره تلفن، نام)
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(customer__phone__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    
    # فیلتر تاریخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # محدود کردن به 100 سفارش (پیجینیشن بعداً)
    orders = orders[:100]
    
    # آمار
    total_count = Order.objects.count()
    pending_count = Order.objects.filter(status='pending').count()
    confirmed_count = Order.objects.filter(status='confirmed').count()
    delivered_count = Order.objects.filter(status='delivered').count()
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'total_count': total_count,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'delivered_count': delivered_count,
        'current_status': status,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/orders_manage.html', context)


@login_required
def order_detail_admin(request, order_id):
    """جزئیات سفارش - فقط برای staff"""
    if not request.user.is_staff_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('home')
    
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related(
            'items__product',
            'items__size',
            'status_logs__changed_by'
        ),
        id=order_id
    )
    
    # تغییر وضعیت
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status and new_status != order.status:
            old_status = order.status
            
            # ثبت لاگ
            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                notes=notes
            )
            
            # تغییر وضعیت
            order.status = new_status
            order.save()
            
            messages.success(request, f'وضعیت سفارش تغییر کرد.')
            return redirect('dashboard:order_detail_admin', order_id=order.id)
    
    context = {
        'order': order,
        'items': order.items.all(),
        'logs': order.status_logs.all().order_by('-created_at'),
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/order_detail_admin.html', context)


# ===================================================================
#  مدیریت نظرات و امتیازات
# ===================================================================

@login_required
def reviews_manage(request):
    """لیست و مدیریت نظرات کاربران"""
    if not request.user.is_staff_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('dashboard:home')

    reviews = ProductRating.objects.select_related(
        'product', 'user'
    ).order_by('-created_at')

    # فیلتر وضعیت
    status = request.GET.get('status')
    if status:
        reviews = reviews.filter(status=status)

    # فیلتر امتیاز
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)

    # جستجو
    search = request.GET.get('search', '').strip()
    if search:
        reviews = reviews.filter(
            Q(product__name__icontains=search) |
            Q(user__phone__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(comment__icontains=search)
        )

    # آمار
    total_count = ProductRating.objects.count()
    pending_count = ProductRating.objects.filter(status='pending').count()
    approved_count = ProductRating.objects.filter(status='approved').count()
    rejected_count = ProductRating.objects.filter(status='rejected').count()

    context = {
        'reviews': reviews[:200],
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'current_status': status or '',
        'current_rating': rating or '',
        'search': search,
    }

    return render(request, 'dashboard/reviews_manage.html', context)


@login_required
def review_action(request, pk):
    """تغییر وضعیت نظر (تأیید / رد / حذف)"""
    if not request.user.is_staff_user:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)

    review = get_object_or_404(ProductRating, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            review.status = 'approved'
            review.save()
            # بروزرسانی میانگین امتیاز محصول
            _update_product_rating(review.product)
            messages.success(request, f'نظر تأیید شد.')

        elif action == 'reject':
            review.status = 'rejected'
            review.save()
            _update_product_rating(review.product)
            messages.success(request, f'نظر رد شد.')

        elif action == 'delete':
            product = review.product
            review.delete()
            _update_product_rating(product)
            messages.success(request, 'نظر حذف شد.')

    return redirect('dashboard:reviews_manage')


@login_required
def reviews_bulk_action(request):
    """عملیات گروهی روی نظرات"""
    if not request.user.is_staff_user:
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('dashboard:home')

    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        ids = request.POST.getlist('review_ids')

        if ids and action:
            reviews = ProductRating.objects.filter(id__in=ids)
            affected_products = set()

            if action == 'approve':
                for r in reviews:
                    affected_products.add(r.product)
                reviews.update(status='approved')
                messages.success(request, f'{len(ids)} نظر تأیید شد.')

            elif action == 'reject':
                for r in reviews:
                    affected_products.add(r.product)
                reviews.update(status='rejected')
                messages.success(request, f'{len(ids)} نظر رد شد.')

            elif action == 'delete':
                for r in reviews:
                    affected_products.add(r.product)
                reviews.delete()
                messages.success(request, f'{len(ids)} نظر حذف شد.')

            # بروزرسانی میانگین امتیاز محصولات تأثیرگرفته
            for product in affected_products:
                _update_product_rating(product)

    return redirect('dashboard:reviews_manage')


def _update_product_rating(product):
    """بروزرسانی میانگین امتیاز محصول"""
    from django.db.models import Avg
    stats = product.ratings.filter(status='approved').aggregate(
        avg=Avg('rating'),
        cnt=Count('id')
    )
    product.avg_rating = stats['avg'] or 0
    product.rating_count = stats['cnt'] or 0
    product.save(update_fields=['avg_rating', 'rating_count'])


# ===================================================================
#  مدیریت فضای رسانه
# ===================================================================

@login_required
def media_storage(request):
    """مدیریت فضای رسانه — بررسی حجم + حذف اوریجینال‌ها"""
    if not request.user.is_staff_user:
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('dashboard:home')

    import os
    from products.models import ProductImage, ProductVideo
    from django.conf import settings as dj_settings

    media_root = dj_settings.MEDIA_ROOT

    def folder_size(path):
        total = 0
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except OSError:
                        pass
        return total

    def fmt(size_bytes):
        if size_bytes < 1024:
            return f'{size_bytes} B'
        elif size_bytes < 1024 * 1024:
            return f'{size_bytes / 1024:.1f} KB'
        elif size_bytes < 1024 * 1024 * 1024:
            return f'{size_bytes / 1024 / 1024:.1f} MB'
        else:
            return f'{size_bytes / 1024 / 1024 / 1024:.2f} GB'

    originals_path = os.path.join(media_root, 'products', 'originals')
    thumbs_path = os.path.join(media_root, 'products', 'thumbnails')
    featured_path = os.path.join(media_root, 'products', 'featured')
    videos_path = os.path.join(media_root, 'products', 'videos')

    originals_size = folder_size(originals_path)
    thumbs_size = folder_size(thumbs_path)
    featured_size = folder_size(featured_path)
    videos_size = folder_size(videos_path)
    total_media = folder_size(media_root)

    # تعداد فایل‌ها
    def file_count(path):
        count = 0
        if os.path.isdir(path):
            for _, _, files in os.walk(path):
                count += len(files)
        return count

    # تصاویری که اوریجینال دارن و تامبنیل هم دارن (قابل حذف)
    deletable_originals = []
    for img in ProductImage.objects.filter(thumbnail__isnull=False).exclude(thumbnail=''):
        if img.original:
            try:
                orig_path = img.original.path
                if os.path.isfile(orig_path):
                    size = os.path.getsize(orig_path)
                    deletable_originals.append({
                        'id': img.id,
                        'product_name': img.product.name,
                        'product_id': img.product.id,
                        'filename': os.path.basename(orig_path),
                        'size': size,
                        'size_display': fmt(size),
                        'is_primary': img.is_primary,
                        'has_featured': bool(img.featured_image),
                    })
            except Exception:
                pass

    deletable_total = sum(d['size'] for d in deletable_originals)

    # === ویدیوهای اوریجینال قابل حذف ===
    deletable_videos = []
    for vid in ProductVideo.objects.filter(processing_status='completed'):
        if vid.original_file and (vid.video_720p or vid.video_480p):
            try:
                orig_path = vid.original_file.path
                if os.path.isfile(orig_path):
                    size = os.path.getsize(orig_path)
                    deletable_videos.append({
                        'id': vid.id,
                        'product_name': vid.product.name,
                        'product_id': vid.product.id,
                        'filename': os.path.basename(orig_path),
                        'size': size,
                        'size_display': fmt(size),
                        'has_720p': bool(vid.video_720p),
                        'has_480p': bool(vid.video_480p),
                        'duration': vid.get_duration_display() if vid.duration else '--',
                    })
            except Exception:
                pass
    deletable_videos_total = sum(d['size'] for d in deletable_videos)

    # فایل‌های یتیم (orphan) — روی دیسک هستن ولی DB بهشون اشاره نمیکنه
    from products.image_processing import cleanup_orphan_files
    orphan_files = cleanup_orphan_files()
    orphan_total = sum(o['size'] for o in orphan_files)

    # === فایل‌های چت ===
    chat_path = os.path.join(media_root, 'chat', 'attachments')
    chat_size = folder_size(chat_path)
    chat_files_count = file_count(chat_path)
    # لیست فایل‌های چت برای حذف
    chat_files = []
    from live_chat.models import ChatMessage
    for msg in ChatMessage.objects.exclude(attachment='').exclude(attachment__isnull=True):
        try:
            fpath = msg.attachment.path
            if os.path.isfile(fpath):
                fsize = os.path.getsize(fpath)
                chat_files.append({
                    'id': msg.id,
                    'session_name': msg.session.visitor_name,
                    'session_id': msg.session.pk,
                    'filename': os.path.basename(fpath),
                    'size': fsize,
                    'size_display': fmt(fsize),
                    'msg_type': msg.msg_type,
                    'is_admin': msg.is_admin,
                    'time': msg.jalali_time,
                })
        except Exception:
            pass
    chat_files_total = sum(f['size'] for f in chat_files)

    # عملیات حذف
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_selected':
            ids = request.POST.getlist('image_ids')
            deleted = 0
            freed = 0
            for img_id in ids:
                try:
                    img = ProductImage.objects.get(pk=img_id)
                    if img.thumbnail and img.original:
                        orig_path = img.original.path
                        if os.path.isfile(orig_path):
                            size = os.path.getsize(orig_path)
                            os.remove(orig_path)
                            img.original = ''
                            img.save(update_fields=['original'])
                            deleted += 1
                            freed += size
                except Exception:
                    pass
            messages.success(request, f'{deleted} فایل اوریجینال حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_all_originals':
            deleted = 0
            freed = 0
            for img in ProductImage.objects.filter(thumbnail__isnull=False).exclude(thumbnail=''):
                if img.original:
                    try:
                        orig_path = img.original.path
                        if os.path.isfile(orig_path):
                            size = os.path.getsize(orig_path)
                            os.remove(orig_path)
                            img.original = ''
                            img.save(update_fields=['original'])
                            deleted += 1
                            freed += size
                    except Exception:
                        pass
            messages.success(request, f'{deleted} فایل اوریجینال حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'cleanup_orphans':
            from products.image_processing import delete_orphan_files
            deleted, freed = delete_orphan_files()
            messages.success(request, f'{deleted} فایل یتیم حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_video_originals':
            ids = request.POST.getlist('video_ids')
            if not ids:
                # حذف همه
                ids = [str(d['id']) for d in deletable_videos]
            deleted = 0
            freed = 0
            for vid_id in ids:
                try:
                    vid = ProductVideo.objects.get(pk=vid_id)
                    if vid.original_file and (vid.video_720p or vid.video_480p):
                        orig_path = vid.original_file.path
                        if os.path.isfile(orig_path):
                            size = os.path.getsize(orig_path)
                            os.remove(orig_path)
                            vid.original_file = ''
                            vid.save(update_fields=['original_file'])
                            deleted += 1
                            freed += size
                except Exception:
                    pass
            messages.success(request, f'{deleted} ویدیوی اوریجینال حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_selected_videos':
            ids = request.POST.getlist('video_ids')
            deleted = 0
            freed = 0
            for vid_id in ids:
                try:
                    vid = ProductVideo.objects.get(pk=vid_id)
                    if vid.original_file and (vid.video_720p or vid.video_480p):
                        orig_path = vid.original_file.path
                        if os.path.isfile(orig_path):
                            size = os.path.getsize(orig_path)
                            os.remove(orig_path)
                            vid.original_file = ''
                            vid.save(update_fields=['original_file'])
                            deleted += 1
                            freed += size
                except Exception:
                    pass
            messages.success(request, f'{deleted} ویدیوی اوریجینال حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_all_video_originals':
            deleted = 0
            freed = 0
            for vid in ProductVideo.objects.filter(processing_status='completed'):
                if vid.original_file and (vid.video_720p or vid.video_480p):
                    try:
                        orig_path = vid.original_file.path
                        if os.path.isfile(orig_path):
                            size = os.path.getsize(orig_path)
                            os.remove(orig_path)
                            vid.original_file = ''
                            vid.save(update_fields=['original_file'])
                            deleted += 1
                            freed += size
                    except Exception:
                        pass
            messages.success(request, f'{deleted} ویدیوی اوریجینال حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_chat_selected':
            ids = request.POST.getlist('chat_ids')
            deleted = 0
            freed = 0
            for msg_id in ids:
                try:
                    msg = ChatMessage.objects.get(pk=msg_id)
                    if msg.attachment:
                        fpath = msg.attachment.path
                        if os.path.isfile(fpath):
                            freed += os.path.getsize(fpath)
                            os.remove(fpath)
                        msg.attachment = ''
                        msg.save(update_fields=['attachment'])
                        deleted += 1
                except Exception:
                    pass
            messages.success(request, f'{deleted} فایل چت حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

        elif action == 'delete_all_chat_files':
            deleted = 0
            freed = 0
            for msg in ChatMessage.objects.exclude(attachment='').exclude(attachment__isnull=True):
                try:
                    fpath = msg.attachment.path
                    if os.path.isfile(fpath):
                        freed += os.path.getsize(fpath)
                        os.remove(fpath)
                    msg.attachment = ''
                    msg.save(update_fields=['attachment'])
                    deleted += 1
                except Exception:
                    pass
            messages.success(request, f'{deleted} فایل چت حذف شد. {fmt(freed)} آزاد شد.')
            return redirect('dashboard:media_storage')

    context = {
        'originals_size': fmt(originals_size),
        'thumbs_size': fmt(thumbs_size),
        'featured_size': fmt(featured_size),
        'videos_size': fmt(videos_size),
        'total_media': fmt(total_media),
        'originals_count': file_count(originals_path),
        'thumbs_count': file_count(thumbs_path),
        'featured_count': file_count(featured_path),
        'videos_count': file_count(videos_path),
        'deletable_originals': deletable_originals,
        'deletable_total': fmt(deletable_total),
        'deletable_count': len(deletable_originals),
        'originals_size_raw': originals_size,
        'thumbs_size_raw': thumbs_size,
        'featured_size_raw': featured_size,
        'videos_size_raw': videos_size,
        'orphan_files': orphan_files,
        'orphan_count': len(orphan_files),
        'orphan_total': fmt(orphan_total),
        'deletable_videos': deletable_videos,
        'deletable_videos_count': len(deletable_videos),
        'deletable_videos_total': fmt(deletable_videos_total),
        'chat_size': fmt(chat_size),
        'chat_files_count': chat_files_count,
        'chat_files': chat_files,
        'chat_files_db_count': len(chat_files),
        'chat_files_total': fmt(chat_files_total),
    }

    return render(request, 'dashboard/media_storage.html', context)


@login_required
def live_alerts_api(request):
    """ایپیای نوتیفیکیشن زنده برای داشبورد مدیریت"""
    if not request.user.is_staff_user:
        return JsonResponse({'error': 'unauthorized'}, status=403)

    from live_chat.models import ChatSession
    from live_chat.models import Ticket

    open_chats = ChatSession.objects.filter(status='open').count()
    pending_orders = Order.objects.filter(status='pending').count()
    open_tickets = Ticket.objects.filter(status__in=['open', 'in_progress']).count()
    pending_reviews = 0
    try:
        from products.models import ProductRating
        pending_reviews = ProductRating.objects.filter(status='pending').count()
    except Exception:
        pass

    total = open_chats + pending_orders + open_tickets + pending_reviews

    return JsonResponse({
        'total': total,
        'chats': open_chats,
        'orders': pending_orders,
        'tickets': open_tickets,
        'reviews': pending_reviews,
    })
