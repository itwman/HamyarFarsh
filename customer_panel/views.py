"""
فاز 9: پنل کاربری مشتری
- داشبورد مشتری
- تاریخچه سفارشات
- مدیریت آدرس‌ها
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum

from orders.models import Order
from accounts.models import Address


@login_required
def customer_dashboard(request):
    """داشبورد مشتری"""
    user = request.user
    
    # آمار سفارشات
    total_orders = Order.objects.filter(customer=user).count()
    pending_orders = Order.objects.filter(customer=user, status='pending').count()
    completed_orders = Order.objects.filter(customer=user, status='delivered').count()
    
    # مبلغ کل خرید
    total_spent = Order.objects.filter(
        customer=user,
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # آخرین سفارشات (5 تا)
    recent_orders = Order.objects.filter(
        customer=user
    ).select_related('shipping_address').prefetch_related(
        'items__product'
    ).order_by('-created_at')[:5]
    
    # آدرس‌های ثبت شده
    addresses_count = Address.objects.filter(user=user).count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'addresses_count': addresses_count,
    }
    
    return render(request, 'customer_panel/dashboard.html', context)


@login_required
def orders_history(request):
    """تاریخچه سفارشات مشتری"""
    orders = Order.objects.filter(
        customer=request.user
    ).select_related('shipping_address').prefetch_related(
        'items__product__album__manufacturer'
    ).order_by('-created_at')
    
    # فیلتر وضعیت
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # صفحه‌بندی
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders_page = paginator.get_page(page)
    
    context = {
        'orders': orders_page,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    }
    
    return render(request, 'customer_panel/orders_history.html', context)


@login_required
def order_detail(request, pk):
    """جزئیات سفارش"""
    order = get_object_or_404(
        Order.objects.select_related(
            'shipping_address'
        ).prefetch_related(
            'items__product__album__manufacturer',
            'items__product__images'
        ),
        pk=pk,
        customer=request.user  # فقط سفارشات خود کاربر
    )
    
    context = {'order': order}
    return render(request, 'customer_panel/order_detail.html', context)


@login_required
def addresses_list(request):
    """لیست آدرس‌های مشتری"""
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {'addresses': addresses}
    return render(request, 'customer_panel/addresses_list.html', context)


@login_required
def address_add(request):
    """افزودن آدرس جدید"""
    if request.method == 'POST':
        province = request.POST.get('province')
        city = request.POST.get('city')
        full_address = request.POST.get('full_address')
        postal_code = request.POST.get('postal_code', '')
        phone = request.POST.get('phone', '')
        is_default = request.POST.get('is_default') == 'on'
        
        # ایجاد آدرس
        Address.objects.create(
            user=request.user,
            province=province,
            city=city,
            full_address=full_address,
            postal_code=postal_code,
            phone=phone,
            is_default=is_default
        )
        
        messages.success(request, 'آدرس با موفقیت اضافه شد.')
        return redirect('customer_panel:addresses_list')
    
    return render(request, 'customer_panel/address_form.html')


@login_required
def address_edit(request, pk):
    """ویرایش آدرس"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.province = request.POST.get('province')
        address.city = request.POST.get('city')
        address.full_address = request.POST.get('full_address')
        address.postal_code = request.POST.get('postal_code', '')
        address.phone = request.POST.get('phone', '')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        
        messages.success(request, 'آدرس با موفقیت ویرایش شد.')
        return redirect('customer_panel:addresses_list')
    
    context = {'address': address}
    return render(request, 'customer_panel/address_form.html', context)


@login_required
def address_delete(request, pk):
    """حذف آدرس"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'آدرس با موفقیت حذف شد.')
        return redirect('customer_panel:addresses_list')
    
    context = {'address': address}
    return render(request, 'customer_panel/address_delete.html', context)


@login_required
def address_set_default(request, pk):
    """تنظیم آدرس پیش‌فرض"""
    if request.method == 'POST':
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.is_default = True
        address.save()  # save method خودش بقیه را غیرفعال می‌کند
        
        messages.success(request, 'آدرس پیش‌فرض تنظیم شد.')
    
    return redirect('customer_panel:addresses_list')


@login_required
def profile_edit(request):
    """ویرایش پروفایل"""
    user = request.user
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # تغییر رمز عبور (اختیاری)
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            messages.warning(request, 'رمز عبور تغییر کرد. لطفاً دوباره وارد شوید.')
        
        user.save()
        messages.success(request, 'پروفایل شما با موفقیت به‌روزرسانی شد.')
        return redirect('customer_panel:dashboard')
    
    context = {'user': user}
    return render(request, 'customer_panel/profile_edit.html', context)
