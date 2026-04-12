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
