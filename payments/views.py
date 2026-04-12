from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from decimal import Decimal
from datetime import date, timedelta
import uuid

from orders.models import Order
from .models import Transaction, PaymentGateway, InstallmentPlan, Installment
from .zarinpal import ZarinpalGateway
from .forms import InstallmentCalculatorForm, InstallmentPlanForm, CheckDetailsForm
from settings_app.models import SiteSettings


def generate_tracking_code():
    """تولید کد پیگیری یکتا"""
    return str(uuid.uuid4())[:13].upper()


# ==================== فاز 8.1: پرداخت آنلاین ====================

@login_required
def payment_request(request, order_id):
    """درخواست پرداخت"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # بررسی وضعیت سفارش
    if order.payment_status == 'paid':
        messages.warning(request, 'این سفارش قبلاً پرداخت شده است.')
        return redirect('orders:detail', order_id=order.id)
    
    # محاسبه مبلغ قابل پرداخت
    amount = order.get_payable_amount()
    
    # دریافت درگاه فعال
    gateway = PaymentGateway.objects.filter(is_active=True).first()
    if not gateway:
        messages.error(request, 'در حال حاضر درگاه پرداختی فعال نیست.')
        return redirect('orders:detail', order_id=order.id)
    
    # ایجاد تراکنش
    tracking_code = generate_tracking_code()
    transaction = Transaction.objects.create(
        order=order,
        gateway=gateway,
        amount=amount,
        tracking_code=tracking_code,
        status='pending',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # ایجاد درخواست پرداخت به درگاه
    if gateway.name == 'zarinpal':
        zp = ZarinpalGateway(
            merchant_id=gateway.merchant_id,
            sandbox=gateway.is_sandbox
        )
        
        callback_url = request.build_absolute_uri(reverse('payments:callback'))
        result = zp.payment_request(
            amount=int(amount),
            description=f'پرداخت سفارش #{order.id}',
            callback_url=callback_url,
            mobile=request.user.phone_number if hasattr(request.user, 'phone_number') else None
        )
        
        if result['status'] == 'success':
            # ذخیره Authority
            transaction.authority = result['authority']
            transaction.status = 'processing'
            transaction.save()
            
            # هدایت به درگاه
            return redirect(result['payment_url'])
        else:
            transaction.mark_as_failed(result['message'])
            messages.error(request, f'خطا در اتصال به درگاه: {result["message"]}')
            return redirect('orders:detail', order_id=order.id)
    
    messages.error(request, 'درگاه پرداخت پشتیبانی نمی‌شود.')
    return redirect('orders:detail', order_id=order.id)


def payment_callback(request):
    """Callback از درگاه پرداخت"""
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    if not authority:
        messages.error(request, 'اطلاعات پرداخت دریافت نشد.')
        return redirect('orders:list')
    
    # یافتن تراکنش
    try:
        transaction = Transaction.objects.get(authority=authority)
    except Transaction.DoesNotExist:
        messages.error(request, 'تراکنش یافت نشد.')
        return redirect('orders:list')
    
    # بررسی وضعیت
    if status == 'OK':
        return redirect('payments:verify', tracking_code=transaction.tracking_code)
    else:
        transaction.mark_as_failed('کاربر پرداخت را لغو کرد.')
        return redirect('payments:failed', tracking_code=transaction.tracking_code)


@login_required
def payment_verify(request, tracking_code):
    """تأیید پرداخت"""
    transaction = get_object_or_404(Transaction, tracking_code=tracking_code)
    
    # بررسی مالکیت
    if transaction.order.user != request.user:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('orders:list')
    
    # اگر قبلاً تأیید شده
    if transaction.status == 'completed':
        return redirect('payments:success', tracking_code=tracking_code)
    
    # تأیید با درگاه
    gateway = transaction.gateway
    if gateway.name == 'zarinpal':
        zp = ZarinpalGateway(
            merchant_id=gateway.merchant_id,
            sandbox=gateway.is_sandbox
        )
        
        result = zp.payment_verify(
            authority=transaction.authority,
            amount=int(transaction.amount)
        )
        
        if result['status'] == 'success':
            # تأیید موفق
            transaction.mark_as_completed(
                reference_number=result['ref_id'],
                gateway_response=result
            )
            
            # بروزرسانی سفارش
            order = transaction.order
            order.payment_status = 'paid' if order.payment_method == 'online_full' else 'partial'
            order.paid_amount += transaction.amount
            order.save()
            
            return redirect('payments:success', tracking_code=tracking_code)
        else:
            transaction.mark_as_failed(result['message'])
            return redirect('payments:failed', tracking_code=tracking_code)
    
    messages.error(request, 'درگاه پرداخت پشتیبانی نمی‌شود.')
    return redirect('orders:detail', order_id=transaction.order.id)


def payment_success(request, tracking_code):
    """صفحه موفقیت پرداخت"""
    transaction = get_object_or_404(Transaction, tracking_code=tracking_code, status='completed')
    
    context = {
        'transaction': transaction,
        'order': transaction.order,
    }
    return render(request, 'payments/success.html', context)


def payment_failed(request, tracking_code):
    """صفحه خطای پرداخت"""
    transaction = get_object_or_404(Transaction, tracking_code=tracking_code)
    
    context = {
        'transaction': transaction,
        'order': transaction.order,
    }
    return render(request, 'payments/failed.html', context)


# ==================== فاز 8.2: سیستم اقساطی ====================

def installment_calculator_view(request):
    """صفحه محاسبه‌گر اقساط برای مشتریان"""
    form = InstallmentCalculatorForm()
    result = None
    
    if request.method == 'POST':
        form = InstallmentCalculatorForm(request.POST)
        if form.is_valid():
            result = calculate_installment(form.cleaned_data)
    
    context = {
        'form': form,
        'result': result,
    }
    return render(request, 'payments/installment_calculator.html', context)


def calculate_installment(data):
    """محاسبه اقساط"""
    total_amount = data['total_amount']
    down_payment = data.get('down_payment', 0)
    plan_type = data['plan_type']
    num_installments = data['num_installments']
    period = data['period']
    
    # دریافت نرخ سود از تنظیمات
    settings_obj = SiteSettings.get_solo()
    
    if plan_type == 'check':
        interest_rate = settings_obj.check_monthly_interest_rate
    else:  # beta
        interest_rate = settings_obj.beta_monthly_interest_rate
    
    # محاسبه مبلغ قابل اقساط
    financed_amount = total_amount - down_payment
    
    # بررسی سقف
    if financed_amount > settings_obj.installment_max:
        return {
            'error': True,
            'message': f'مبلغ قابل اقساط ({financed_amount:,} تومان) از سقف مجاز ({settings_obj.installment_max:,} تومان) بیشتر است. '
                      f'لطفاً پیش‌پرداخت را افزایش دهید یا مبلغ اضافی را نقدی پرداخت کنید.'
        }
    
    # محاسبه تعداد ماه‌ها
    months = num_installments if period == 'monthly' else num_installments * 2
    
    # محاسبه سود
    total_interest = financed_amount * (interest_rate / 100) * months
    total_with_interest = financed_amount + total_interest
    installment_amount = int(total_with_interest / num_installments)
    
    return {
        'error': False,
        'total_amount': total_amount,
        'down_payment': down_payment,
        'financed_amount': financed_amount,
        'interest_rate': interest_rate,
        'months': months,
        'total_interest': total_interest,
        'total_with_interest': total_with_interest,
        'num_installments': num_installments,
        'installment_amount': installment_amount,
        'period_display': 'ماهانه' if period == 'monthly' else 'دوماهانه',
        'plan_type_display': 'چک صیادی' if plan_type == 'check' else 'طرح بتا (بانک رفاه)',
    }


def installment_calculator_ajax(request):
    """API محاسبه اقساط (AJAX)"""
    if request.method == 'POST':
        form = InstallmentCalculatorForm(request.POST)
        if form.is_valid():
            result = calculate_installment(form.cleaned_data)
            return JsonResponse(result)
        else:
            return JsonResponse({'error': True, 'message': 'داده‌های ورودی نامعتبر است.'})
    
    return JsonResponse({'error': True, 'message': 'درخواست نامعتبر'})


@staff_member_required
def create_installment_plan(request, order_id):
    """ایجاد طرح اقساط برای سفارش"""
    order = get_object_or_404(Order, id=order_id)
    
    # بررسی وجود طرح قبلی
    if hasattr(order, 'installment_plan'):
        messages.warning(request, 'این سفارش قبلاً دارای طرح اقساط است.')
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        form = InstallmentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.order = order
            plan.save()
            
            # ایجاد اقساط تفکیکی
            generate_installments(plan)
            
            messages.success(request, 'طرح اقساط با موفقیت ایجاد شد.')
            return redirect('payments:installment_detail', plan_id=plan.id)
    else:
        initial_data = {
            'total_amount': order.total_amount,
            'down_payment': 0,
            'num_installments': 12,
            'period': 'monthly',
        }
        
        # نرخ سود پیش‌فرض
        settings_obj = SiteSettings.get_solo()
        initial_data['interest_rate'] = settings_obj.check_monthly_interest_rate
        
        form = InstallmentPlanForm(initial=initial_data)
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'payments/create_installment_plan.html', context)


def generate_installments(plan):
    """تولید اقساط تفکیکی برای یک طرح"""
    first_due = plan.first_due_date or date.today() + timedelta(days=30)
    
    # محاسبه فاصله بین اقساط (ماهانه یا دوماهانه)
    interval_days = 30 if plan.period == 'monthly' else 60
    
    for i in range(1, plan.num_installments + 1):
        due_date = first_due + timedelta(days=(i - 1) * interval_days)
        
        Installment.objects.create(
            plan=plan,
            installment_number=i,
            amount=plan.installment_amount,
            due_date=due_date,
            status='pending'
        )


@login_required
def installment_plan_detail(request, plan_id):
    """جزئیات طرح اقساط"""
    plan = get_object_or_404(InstallmentPlan, id=plan_id)
    
    # بررسی دسترسی
    if not (request.user == plan.order.user or request.user.is_staff):
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('orders:list')
    
    installments = plan.installments.all()
    
    # بررسی اقساط سررسید گذشته
    for inst in installments:
        if inst.is_overdue() and inst.status == 'pending':
            inst.status = 'overdue'
            inst.save()
    
    context = {
        'plan': plan,
        'installments': installments,
        'order': plan.order,
    }
    return render(request, 'payments/installment_detail.html', context)


@staff_member_required
def confirm_installment_plan(request, plan_id):
    """تأیید طرح اقساط توسط مدیر"""
    plan = get_object_or_404(InstallmentPlan, id=plan_id)
    
    if request.method == 'POST':
        plan.is_confirmed = True
        plan.confirmed_at = timezone.now()
        plan.confirmed_by = request.user
        plan.save()
        
        # بروزرسانی وضعیت سفارش
        order = plan.order
        order.payment_status = 'installment'
        order.save()
        
        messages.success(request, 'طرح اقساط تأیید شد.')
        return redirect('payments:installment_detail', plan_id=plan.id)
    
    context = {
        'plan': plan,
    }
    return render(request, 'payments/confirm_installment.html', context)


# ==================== فاز 8.3: فاکتور و قیمت روز ====================

@login_required
def invoice_view(request, order_id):
    """نمایش فاکتور سفارش"""
    order = get_object_or_404(Order, id=order_id)
    
    # بررسی دسترسی
    if not (request.user == order.user or request.user.is_staff):
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('orders:list')
    
    # محاسبه قیمت‌ها
    current_prices = {}
    price_changes = {}
    
    if order.payment_method == 'deposit_on_delivery':
        # برای بیعانه‌ها، قیمت روز را محاسبه می‌کنیم
        for item in order.items.all():
            current_price = item.product.get_price_for_size(item.size)
            original_price = item.unit_price
            
            current_prices[item.id] = current_price
            
            if current_price != original_price:
                price_changes[item.id] = {
                    'original': original_price,
                    'current': current_price,
                    'difference': current_price - original_price,
                    'percentage': ((current_price - original_price) / original_price * 100) if original_price > 0 else 0
                }
        
        # محاسبه مبلغ جدید
        new_total = sum(current_prices[item.id] * item.quantity for item in order.items.all())
        new_remaining = new_total - order.paid_amount
    else:
        new_total = order.total_amount
        new_remaining = order.remaining_amount
    
    context = {
        'order': order,
        'current_prices': current_prices,
        'price_changes': price_changes,
        'new_total': new_total,
        'new_remaining': new_remaining,
        'has_price_change': bool(price_changes),
    }
    return render(request, 'payments/invoice.html', context)


@login_required
def invoice_pdf(request, order_id):
    """دانلود فاکتور PDF"""
    order = get_object_or_404(Order, id=order_id)
    
    # بررسی دسترسی
    if not (request.user == order.user or request.user.is_staff):
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('orders:list')
    
    # TODO: ایجاد PDF با ReportLab یا WeasyPrint
    # فعلاً پیام ساده
    messages.info(request, 'قابلیت دانلود PDF فاکتور به زودی اضافه می‌شود.')
    return redirect('payments:invoice', order_id=order_id)


@staff_member_required
def apply_current_prices(request, order_id):
    """اعمال قیمت روز به سفارش (فقط مدیر)"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.payment_method != 'deposit_on_delivery':
        messages.warning(request, 'این عملیات فقط برای سفارش‌های بیعانه‌ای مجاز است.')
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        # ذخیره قیمت‌های قبلی در گزارش
        price_report = []
        
        for item in order.items.all():
            old_price = item.unit_price
            current_price = item.product.get_price_for_size(item.size)
            
            if old_price != current_price:
                price_report.append({
                    'product': item.product.name,
                    'size': item.size.name,
                    'old_price': old_price,
                    'new_price': current_price,
                    'difference': current_price - old_price,
                })
                
                # بروزرسانی قیمت
                item.unit_price = current_price
                item.save()
        
        # محاسبه مجدد مبالغ سفارش
        order.calculate_totals()
        order.save()
        
        # ایجاد لاگ
        if price_report:
            messages.success(
                request, 
                f'قیمت‌های سفارش به روز شد. تعداد {len(price_report)} آیتم تغییر قیمت داشت.'
            )
        else:
            messages.info(request, 'قیمت‌ها تغییری نداشتند.')
        
        return redirect('payments:invoice', order_id=order.id)
    
    # نمایش پیش‌نمایش تغییرات
    price_preview = []
    for item in order.items.all():
        current_price = item.product.get_price_for_size(item.size)
        if item.unit_price != current_price:
            price_preview.append({
                'item': item,
                'old_price': item.unit_price,
                'new_price': current_price,
                'difference': current_price - item.unit_price,
            })
    
    context = {
        'order': order,
        'price_preview': price_preview,
    }
    return render(request, 'payments/confirm_price_update.html', context)
