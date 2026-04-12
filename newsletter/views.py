"""
فاز 20: ویوهای خبرنامه پیامکی
- فرم عضویت فوتر (AJAX)
- پنل مدیریت مشترکین
- کمپین ارسال انبوه
"""
import re
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from .models import NewsletterSubscriber, SMSCampaign, CampaignLog
from .forms import SubscribeForm, SMSCampaignForm, BulkAddForm


# ===================================================================
#  فرم عضویت فوتر — AJAX
# ===================================================================

@require_POST
def subscribe_ajax(request):
    """عضویت خبرنامه از فوتر — AJAX"""
    form = SubscribeForm(request.POST)
    if not form.is_valid():
        errors = '; '.join([e for errs in form.errors.values() for e in errs])
        return JsonResponse({'success': False, 'message': errors})

    phone = form.cleaned_data['phone']
    name = form.cleaned_data.get('name', '')

    # بررسی تکراری
    existing = NewsletterSubscriber.objects.filter(phone=phone).first()
    if existing:
        if existing.status == 'unsubscribed':
            existing.status = 'active'
            existing.save(update_fields=['status'])
            return JsonResponse({'success': True, 'message': 'عضویت شما مجدداً فعال شد!'})
        return JsonResponse({'success': False, 'message': 'این شماره قبلاً ثبت شده است.'})

    # ایجاد مشترک
    sub = NewsletterSubscriber.objects.create(
        phone=phone, name=name, source='footer',
        user=request.user if request.user.is_authenticated else None
    )

    # ارسال پیام تبریک خودکار
    _send_welcome_sms(sub)

    return JsonResponse({
        'success': True,
        'message': 'عضویت شما با موفقیت انجام شد! پیامک خوش‌آمدگویی ارسال شد.'
    })


def _send_welcome_sms(subscriber):
    """ارسال پیامک خوش‌آمدگویی"""
    from settings_app.models import SiteSettings
    from notifications.services import send_sms

    ss = SiteSettings.get_solo()
    welcome_text = getattr(ss, 'newsletter_welcome_sms', '')
    if not welcome_text:
        welcome_text = f'{subscriber.name or "مشتری عزیز"} خوش آمدید!\nاز عضویت شما در خبرنامه {ss.site_name} متشکریم.\nبرای اطلاع از تخفیف‌ها و محصولات جدید با ما همراه باشید.'

    welcome_text = welcome_text.replace('{name}', subscriber.name or 'مشتری عزیز')
    welcome_text = welcome_text.replace('{site_name}', ss.site_name)

    send_sms(subscriber.phone, welcome_text, event='newsletter_welcome')


def unsubscribe(request, phone):
    """لغو عضویت"""
    try:
        sub = NewsletterSubscriber.objects.get(phone=phone)
        sub.status = 'unsubscribed'
        sub.unsubscribed_at = timezone.now()
        sub.save(update_fields=['status', 'unsubscribed_at'])
        return render(request, 'newsletter/unsubscribed.html')
    except NewsletterSubscriber.DoesNotExist:
        return render(request, 'newsletter/unsubscribed.html')


# ===================================================================
#  پنل مدیریت مشترکین
# ===================================================================

@staff_member_required
def admin_dashboard(request):
    """داشبورد خبرنامه"""
    subs = NewsletterSubscriber.objects.all()

    # فیلتر
    status = request.GET.get('status', '')
    if status:
        subs = subs.filter(status=status)
    source = request.GET.get('source', '')
    if source:
        subs = subs.filter(source=source)
    q = request.GET.get('q', '').strip()
    if q:
        subs = subs.filter(Q(phone__icontains=q) | Q(name__icontains=q))

    # آمار
    total = NewsletterSubscriber.objects.count()
    active = NewsletterSubscriber.objects.filter(status='active').count()
    today = NewsletterSubscriber.objects.filter(
        subscribed_at__date=timezone.now().date()
    ).count()

    campaigns = SMSCampaign.objects.all()[:5]

    context = {
        'subscribers': subs[:100],
        'total': total,
        'active': active,
        'today': today,
        'campaigns': campaigns,
        'query': q,
        'current_status': status,
        'current_source': source,
    }
    return render(request, 'newsletter/admin_dashboard.html', context)


@staff_member_required
def subscriber_delete(request, pk):
    sub = get_object_or_404(NewsletterSubscriber, pk=pk)
    if request.method == 'POST':
        sub.delete()
        messages.success(request, f'شماره {sub.phone} حذف شد.')
    return redirect('newsletter:admin_dashboard')


@staff_member_required
def subscriber_toggle(request, pk):
    sub = get_object_or_404(NewsletterSubscriber, pk=pk)
    if sub.status == 'active':
        sub.status = 'unsubscribed'
        sub.unsubscribed_at = timezone.now()
    else:
        sub.status = 'active'
        sub.unsubscribed_at = None
    sub.save(update_fields=['status', 'unsubscribed_at'])
    messages.success(request, f'وضعیت {sub.phone} تغییر کرد.')
    return redirect('newsletter:admin_dashboard')


@staff_member_required
def bulk_add(request):
    """افزودن دستی شماره‌ها"""
    if request.method == 'POST':
        form = BulkAddForm(request.POST)
        if form.is_valid():
            phones_text = form.cleaned_data['phones']
            lines = [l.strip() for l in phones_text.split('\n') if l.strip()]
            added = 0
            skipped = 0
            for line in lines:
                phone = re.sub(r'\D', '', line)
                if re.match(r'^09\d{9}$', phone):
                    _, created = NewsletterSubscriber.objects.get_or_create(
                        phone=phone,
                        defaults={'source': 'manual', 'status': 'active'}
                    )
                    if created:
                        added += 1
                    else:
                        skipped += 1
            messages.success(request, f'{added} شماره اضافه شد. {skipped} تکراری رد شد.')
            return redirect('newsletter:admin_dashboard')
    else:
        form = BulkAddForm()
    return render(request, 'newsletter/bulk_add.html', {'form': form})


@staff_member_required
def bulk_import(request):
    """واردکردن از فایل CSV/TXT"""
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        content = f.read().decode('utf-8', errors='ignore')
        lines = content.strip().split('\n')
        added = 0
        for line in lines:
            phone = re.sub(r'\D', '', line.strip().split(',')[0].split('\t')[0])
            if re.match(r'^09\d{9}$', phone):
                _, created = NewsletterSubscriber.objects.get_or_create(
                    phone=phone,
                    defaults={'source': 'import', 'status': 'active'}
                )
                if created:
                    added += 1
        messages.success(request, f'{added} شماره از فایل وارد شد.')
        return redirect('newsletter:admin_dashboard')
    return render(request, 'newsletter/bulk_import.html')


@staff_member_required
def export_csv(request):
    """خروجی CSV مشترکین"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
    response.write('\ufeff')  # BOM for Excel
    writer = csv.writer(response)
    writer.writerow(['شماره موبایل', 'نام', 'وضعیت', 'منبع', 'تاریخ عضویت'])
    for sub in NewsletterSubscriber.objects.filter(status='active').order_by('-subscribed_at'):
        writer.writerow([sub.phone, sub.name, sub.get_status_display(),
                         sub.get_source_display(), sub.jalali_subscribed])
    return response


# ===================================================================
#  کمپین ارسال انبوه
# ===================================================================

@staff_member_required
def campaign_list(request):
    campaigns = SMSCampaign.objects.all()
    return render(request, 'newsletter/campaign_list.html', {'campaigns': campaigns})


@staff_member_required
def campaign_create(request):
    if request.method == 'POST':
        form = SMSCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()
            messages.success(request, f'کمپین «{campaign.title}» ایجاد شد.')
            return redirect('newsletter:campaign_detail', pk=campaign.pk)
    else:
        form = SMSCampaignForm()
    return render(request, 'newsletter/campaign_form.html', {
        'form': form, 'title': 'ایجاد کمپین', 'is_edit': False
    })


@staff_member_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(SMSCampaign, pk=pk)
    if campaign.status != 'draft':
        messages.error(request, 'فقط کمپین‌های پیش‌نویس قابل ویرایش هستند.')
        return redirect('newsletter:campaign_detail', pk=pk)
    if request.method == 'POST':
        form = SMSCampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'کمپین بروزرسانی شد.')
            return redirect('newsletter:campaign_detail', pk=pk)
    else:
        form = SMSCampaignForm(instance=campaign)
    return render(request, 'newsletter/campaign_form.html', {
        'form': form, 'campaign': campaign, 'title': f'ویرایش: {campaign.title}', 'is_edit': True
    })


@staff_member_required
def campaign_detail(request, pk):
    """جزئیات و پیش‌نمایش کمپین"""
    campaign = get_object_or_404(SMSCampaign, pk=pk)
    recipients = campaign.get_recipients()
    preview_text = campaign.render_message()
    logs = campaign.logs.all()[:50]

    context = {
        'campaign': campaign,
        'recipient_count': recipients.count(),
        'preview_text': preview_text,
        'char_count': len(preview_text),
        'logs': logs,
    }
    return render(request, 'newsletter/campaign_detail.html', context)


@staff_member_required
@require_POST
def campaign_send(request, pk):
    """ارسال کمپین"""
    campaign = get_object_or_404(SMSCampaign, pk=pk)
    if campaign.status != 'draft':
        messages.error(request, 'این کمپین قبلاً ارسال شده.')
        return redirect('newsletter:campaign_detail', pk=pk)

    from notifications.services import send_sms

    recipients = campaign.get_recipients()
    campaign.status = 'sending'
    campaign.total_recipients = recipients.count()
    campaign.sent_at = timezone.now()
    campaign.save()

    sent = 0
    failed = 0
    for sub in recipients:
        text = campaign.render_message(subscriber=sub)
        success = send_sms(sub.phone, text, event=f'campaign_{campaign.pk}')
        CampaignLog.objects.create(
            campaign=campaign,
            phone=sub.phone,
            status='sent' if success else 'failed'
        )
        if success:
            sent += 1
        else:
            failed += 1

    campaign.sent_count = sent
    campaign.failed_count = failed
    campaign.status = 'completed'
    campaign.save()

    messages.success(request, f'کمپین ارسال شد! {sent} موفق، {failed} ناموفق.')
    return redirect('newsletter:campaign_detail', pk=pk)


@staff_member_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(SMSCampaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'کمپین حذف شد.')
    return redirect('newsletter:campaign_list')
