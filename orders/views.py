"""
ویوهای سبد خرید و سفارش
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal

from .cart import Cart
from .models import Order, OrderItem, OrderStatusLog
from .forms import AddToCartForm, CustomSizeOrderForm, CheckoutForm
from products.models import Product
from catalog.models import CarpetSize
from accounts.models import Address
from settings_app.models import SiteSettings


def cart_detail(request):
    """نمایش سبد خرید"""
    cart = Cart(request)
    site_settings = SiteSettings.get_solo()  # ✅ اصلاح شد
    
    # محاسبه هزینه ارسال
    shipping_cost = cart.get_shipping_cost()
    free_shipping = cart.check_free_shipping()
    total_with_shipping = cart.get_total_price() + shipping_cost
    
    context = {
        'cart': cart,
        'cart_items': cart.get_items(),
        'total_price': cart.get_total_price(),
        'shipping_cost': shipping_cost,
        'free_shipping': free_shipping,
        'total_with_shipping': total_with_shipping,
        'min_free_shipping': site_settings.free_shipping_min,
    }
    
    return render(request, 'orders/cart_detail.html', context)


@require_POST
def cart_add(request, product_id):
    """افزودن محصول به سبد"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    size_id = request.POST.get('size_id')
    quantity = int(request.POST.get('quantity', 1))
    is_pair = request.POST.get('is_pair') == 'on'
    
    try:
        size = None
        if size_id:
            size = get_object_or_404(CarpetSize, id=size_id)
        
        # بررسی قانون زوج/فرد
        if size:
            # بررسی override از محصول
            size_rule = product.size_rules.filter(size=size).first()
            if size_rule:
                default_pair = size_rule.order_rule == 'pair_only'
            else:
                default_pair = size.default_order_rule == 'pair_only'
            
            if default_pair and not is_pair:
                messages.warning(request, f'سایز {size.name} باید به صورت زوج سفارش داده شود.')
                is_pair = True
        
        # افزودن به سبد
        cart.add(
            product=product,
            size=size,
            quantity=quantity,
            is_pair=is_pair
        )
        
        messages.success(request, f'{product.name} به سبد خرید اضافه شد.')
        
    except Exception as e:
        messages.error(request, f'خطا در افزودن به سبد: {str(e)}')
    
    # بازگشت به صفحه قبل یا سبد خرید
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


@require_POST
def cart_add_ajax(request):
    """افزودن محصول به سبد - AJAX"""
    try:
        cart = Cart(request)
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(CarpetSize, id=size_id) if size_id else None
        
        # افزودن به سبد
        cart.add(
            product=product,
            size=size,
            quantity=quantity
        )
        
        return JsonResponse({
            'success': True,
            'message': 'محصول به سبد خرید اضافه شد',
            'cart_count': len(cart)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def cart_update(request):
    """بروزرسانی تعداد در سبد - AJAX"""
    cart = Cart(request)
    
    product_id = request.POST.get('product_id')
    size_id = request.POST.get('size_id', 'none')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart.update_quantity(product_id, size_id, quantity)
        
        # محاسبه مجدد
        new_total = cart.get_total_price()
        shipping_cost = cart.get_shipping_cost()
        
        return JsonResponse({
            'success': True,
            'total_price': new_total,
            'shipping_cost': shipping_cost,
            'total_with_shipping': new_total + shipping_cost,
            'free_shipping': cart.check_free_shipping(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_POST
def cart_remove(request):
    """حذف آیتم از سبد"""
    cart = Cart(request)
    
    product_id = request.POST.get('product_id')
    size_id = request.POST.get('size_id', 'none')
    
    try:
        cart.remove(product_id, size_id)
        messages.success(request, 'محصول از سبد خرید حذف شد.')
    except Exception as e:
        messages.error(request, f'خطا در حذف: {str(e)}')
    
    return redirect('orders:cart_detail')


def cart_clear(request):
    """خالی کردن سبد"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'سبد خرید خالی شد.')
    return redirect('orders:cart_detail')


@login_required
def checkout(request):
    """صفحه تکمیل سفارش"""
    cart = Cart(request)
    
    if cart.is_empty():
        messages.warning(request, 'سبد خرید شما خالی است.')
        return redirect('orders:cart_detail')
    
    site_settings = SiteSettings.get_solo()  # ✅ اصلاح شد
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # ایجاد سفارش
                    payment_method = form.cleaned_data['payment_method']
                    shipping_address_id = form.cleaned_data['shipping_address_id']
                    notes = form.cleaned_data.get('notes', '')
                    
                    shipping_address = Address.objects.get(id=shipping_address_id)
                    
                    # محاسبه مبالغ
                    total_amount = cart.get_total_price()
                    shipping_cost = cart.get_shipping_cost(payment_method)
                    total_with_shipping = total_amount + shipping_cost
                    
                    # محاسبه بیعانه
                    deposit_amount = 0
                    is_price_today = False
                    
                    if payment_method == 'deposit_on_delivery':
                        deposit_percent = site_settings.deposit_percent / 100
                        deposit_amount = int(total_with_shipping * deposit_percent)
                        is_price_today = True
                    
                    # ایجاد سفارش
                    order = Order.objects.create(
                        customer=request.user,
                        status='pending',
                        payment_method=payment_method,
                        total_amount=total_with_shipping,
                        deposit_amount=deposit_amount,
                        paid_amount=0,
                        shipping_cost=shipping_cost,
                        shipping_address=shipping_address,
                        notes=notes,
                        is_price_today=is_price_today,
                        free_shipping=(shipping_cost == 0)
                    )
                    
                    # ایجاد آیتم‌های سفارش
                    for item in cart.get_items():
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            size=item['size'],
                            quantity=item['quantity'],
                            unit_price=item['unit_price'],
                            is_pair_order=item['is_pair']
                        )
                    
                    # خالی کردن سبد
                    cart.clear()
                    
                    messages.success(request, f'سفارش شما با موفقیت ثبت شد. شماره سفارش: {order.id}')
                    
                    # هدایت به صفحه پرداخت یا جزئیات سفارش
                    if payment_method == 'online_full':
                        return redirect('orders:order_payment', order_id=order.id)
                    elif payment_method == 'deposit_on_delivery':
                        if deposit_amount > 0:
                            return redirect('orders:order_payment', order_id=order.id)
                    
                    return redirect('orders:order_detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, f'خطا در ثبت سفارش: {str(e)}')
    
    else:
        form = CheckoutForm(user=request.user)
    
    # محاسبات برای نمایش
    total_price = cart.get_total_price()
    shipping_cost = cart.get_shipping_cost()
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.get_items(),
        'addresses': addresses,
        'total_price': total_price,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_price + shipping_cost,
        'site_settings': site_settings,
    }
    
    return render(request, 'orders/checkout.html', context)


def custom_size_order(request, product_id):
    """صفحه سفارش سایز سفارشی"""
    product = get_object_or_404(Product, id=product_id)
    site_settings = SiteSettings.get_solo()  # ✅ اصلاح شد
    
    if request.method == 'POST':
        form = CustomSizeOrderForm(request.POST)
        
        if form.is_valid():
            # ثبت درخواست سایز سفارشی
            # این درخواست باید توسط مدیر بررسی و قیمت‌گذاری شود
            
            length = form.cleaned_data['length']
            width = form.cleaned_data['width']
            quantity = form.cleaned_data['quantity']
            phone = form.cleaned_data['customer_phone']
            notes = form.cleaned_data.get('notes', '')
            
            # ارسال اطلاعیه به مدیر (می‌توان با ایمیل یا SMS انجام داد)
            # یا ذخیره در یک مدل CustomSizeRequest
            
            messages.success(
                request,
                f'درخواست شما برای سایز {length}×{width} به تعداد {quantity} ثبت شد. '
                'کارشناسان ما در اسرع وقت با شما تماس خواهند گرفت.'
            )
            
            return redirect('shop:product_detail', slug=product.slug)
    
    else:
        form = CustomSizeOrderForm(initial={'product_id': product_id})
    
    context = {
        'form': form,
        'product': product,
        'site_settings': site_settings,
    }
    
    return render(request, 'orders/custom_size_order.html', context)


@login_required
def order_detail(request, order_id):
    """نمایش جزئیات سفارش"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.items.select_related('product', 'size')
    status_logs = order.status_logs.select_related('changed_by').all()[:10]
    
    context = {
        'order': order,
        'items': items,
        'status_logs': status_logs,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """لیست سفارشات کاربر"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def order_payment(request, order_id):
    """صفحه پرداخت سفارش"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # بررسی وضعیت سفارش
    if order.status not in ['pending', 'reviewing']:
        messages.warning(request, 'این سفارش قابل پرداخت نیست.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # محاسبه مبلغ قابل پرداخت
    if order.payment_method == 'online_full':
        payable_amount = order.total_amount
    elif order.payment_method == 'deposit_on_delivery':
        payable_amount = order.deposit_amount
    else:
        messages.warning(request, 'این روش پرداخت نیاز به پرداخت آنلاین ندارد.')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'payable_amount': payable_amount,
    }
    
    # اینجا باید اتصال به درگاه پرداخت انجام شود (فاز 8)
    # فعلاً فقط صفحه نمایش داده می‌شود
    
    return render(request, 'orders/order_payment.html', context)


@login_required
@require_POST
def order_cancel(request, order_id):
    """لغو سفارش"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if not order.can_cancel():
        messages.error(request, 'این سفارش قابل لغو نیست.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # محاسبه جریمه انصراف
    penalty = order.calculate_cancellation_penalty()
    
    # تأیید لغو
    confirm = request.POST.get('confirm')
    if confirm == 'yes':
        order.status = 'cancelled'
        order.save()
        
        # ثبت لاگ
        OrderStatusLog.objects.create(
            order=order,
            old_status='pending',
            new_status='cancelled',
            changed_by=request.user,
            notes=f'لغو توسط مشتری. جریمه انصراف: {penalty:,} تومان'
        )
        
        messages.success(request, f'سفارش لغو شد. جریمه انصراف: {penalty:,} تومان')
        return redirect('orders:order_list')
    
    # نمایش صفحه تأیید
    context = {
        'order': order,
        'penalty': penalty,
    }
    
    return render(request, 'orders/order_cancel_confirm.html', context)
