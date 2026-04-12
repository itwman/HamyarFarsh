"""
فاز 17: ویوهای کوپن تخفیف
- پنل مدیریت: CRUD + گزارش
- API: اعتبارسنجی AJAX برای سبد خرید
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from .models import Coupon, CouponUsage
from .forms import CouponForm


# ===================================================================
#  API — اعتبارسنجی کوپن (AJAX از سبد خرید)
# ===================================================================

@require_POST
def apply_coupon(request):
    """اعمال کوپن تخفیف — AJAX"""
    code = request.POST.get('code', '').strip().upper()
    if not code:
        return JsonResponse({'valid': False, 'message': 'کد تخفیف را وارد کنید.'})

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'کد تخفیف نامعتبر است.'})

    # بررسی اعتبار کلی
    if not request.user.is_authenticated:
        return JsonResponse({'valid': False, 'message': 'برای استفاده از کوپن ابتدا وارد شوید.'})

    # دریافت مبلغ سبد از session
    from orders.cart import Cart
    cart = Cart(request)
    order_amount = cart.get_total_price()

    if order_amount == 0:
        return JsonResponse({'valid': False, 'message': 'سبد خرید شما خالی است.'})

    # اعتبارسنجی کامل
    valid, msg = coupon.is_valid_for_order(request.user, order_amount)
    if not valid:
        return JsonResponse({'valid': False, 'message': msg})

    # محاسبه تخفیف
    discount = coupon.calculate_discount(order_amount)

    # ذخیره کوپن در session
    request.session['coupon_id'] = coupon.id
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = discount

    # پیام نمایشی
    if coupon.coupon_type == 'percent':
        desc = f'{coupon.amount}% تخفیف'
        if coupon.max_discount:
            desc += f' (سقف {coupon.max_discount:,} تومان)'
    else:
        desc = f'{coupon.amount:,} تومان تخفیف'

    return JsonResponse({
        'valid': True,
        'message': f'کوپن «{coupon.code}» اعمال شد! {desc}',
        'discount': discount,
        'discount_display': f'{discount:,}',
        'new_total': order_amount - discount,
        'new_total_display': f'{order_amount - discount:,}',
    })


@require_POST
def remove_coupon(request):
    """حذف کوپن از سبد — AJAX"""
    request.session.pop('coupon_id', None)
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    return JsonResponse({'success': True, 'message': 'کوپن حذف شد.'})


# ===================================================================
#  پنل مدیریت
# ===================================================================

@staff_member_required
def coupon_list(request):
    """لیست کوپن‌ها"""
    coupons = Coupon.objects.all()

    # فیلتر
    status = request.GET.get('status', '')
    if status == 'active':
        coupons = coupons.filter(is_active=True)
    elif status == 'expired':
        from django.utils import timezone
        coupons = coupons.filter(end_date__lt=timezone.now())
    elif status == 'inactive':
        coupons = coupons.filter(is_active=False)

    q = request.GET.get('q', '').strip()
    if q:
        coupons = coupons.filter(code__icontains=q)

    # آمار
    total = Coupon.objects.count()
    active = Coupon.objects.filter(is_active=True).count()
    total_usage = CouponUsage.objects.count()
    total_discount_given = CouponUsage.objects.aggregate(s=Sum('discount_amount'))['s'] or 0

    context = {
        'coupons': coupons,
        'total': total,
        'active': active,
        'total_usage': total_usage,
        'total_discount_given': total_discount_given,
        'query': q,
        'current_status': status,
    }
    return render(request, 'coupons/coupon_list.html', context)


@staff_member_required
def coupon_create(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'کوپن «{form.instance.code}» ایجاد شد.')
            return redirect('coupons:coupon_list')
    else:
        form = CouponForm(initial={'code': Coupon.generate_code()})
    return render(request, 'coupons/coupon_form.html', {
        'form': form, 'title': 'ایجاد کوپن تخفیف', 'is_edit': False
    })


@staff_member_required
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, f'کوپن «{coupon.code}» بروزرسانی شد.')
            return redirect('coupons:coupon_list')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'coupons/coupon_form.html', {
        'form': form, 'coupon': coupon, 'title': f'ویرایش: {coupon.code}', 'is_edit': True
    })


@staff_member_required
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'کوپن حذف شد.')
    return redirect('coupons:coupon_list')


@staff_member_required
def coupon_toggle(request, pk):
    """فعال/غیرفعال کردن سریع"""
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.is_active = not coupon.is_active
    coupon.save(update_fields=['is_active'])
    messages.success(request, f'کوپن «{coupon.code}» {"فعال" if coupon.is_active else "غیرفعال"} شد.')
    return redirect('coupons:coupon_list')


@staff_member_required
def coupon_generate_code(request):
    """تولید کد تصادفی — AJAX"""
    code = Coupon.generate_code()
    return JsonResponse({'code': code})


@staff_member_required
def coupon_report(request, pk):
    """گزارش استفاده یک کوپن"""
    coupon = get_object_or_404(Coupon, pk=pk)
    usages = coupon.usages.select_related('user', 'order').order_by('-used_at')
    total_discount = usages.aggregate(s=Sum('discount_amount'))['s'] or 0

    context = {
        'coupon': coupon,
        'usages': usages,
        'total_discount': total_discount,
    }
    return render(request, 'coupons/coupon_report.html', context)
