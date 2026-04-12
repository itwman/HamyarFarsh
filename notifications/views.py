"""
فاز 19: ویوهای اطلاع‌رسانی
- پنل مدیریت: اعلان‌ها + قالب پیامک + لاگ
- API: نوتیفیکیشن‌های کاربر
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Announcement, Notification, SMSTemplate, SMSLog
from .forms import AnnouncementForm, SMSTemplateForm


# ===================================================================
#  API — نوتیفیکیشن کاربر
# ===================================================================

@login_required
def notification_list_api(request):
    """لیست نوتیفیکیشن‌ها — AJAX (dropdown navbar)"""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:15]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message[:80],
        'link': n.link,
        'icon': n.icon,
        'color': n.color,
        'is_read': n.is_read,
        'date': n.jalali_date,
    } for n in notifs]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread})


@login_required
@require_POST
def notification_mark_read(request):
    """خوانده شدن نوتیفیکیشن — AJAX"""
    notif_id = request.POST.get('id')
    if notif_id:
        Notification.objects.filter(pk=notif_id, user=request.user).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
@require_POST
def notification_mark_all_read(request):
    """خوانده شدن همه نوتیفیکیشن‌ها"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def notification_page(request):
    """صفحه همه نوتیفیکیشن‌ها"""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    # خواندن همه
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_page.html', {'notifications': notifs})


# ===================================================================
#  dismiss اعلان (cookie-based)
# ===================================================================

@require_POST
def announcement_dismiss(request):
    """بستن اعلان توسط کاربر — ذخیره در session"""
    ann_id = request.POST.get('id')
    dismissed = request.session.get('dismissed_announcements', [])
    if ann_id and int(ann_id) not in dismissed:
        dismissed.append(int(ann_id))
        request.session['dismissed_announcements'] = dismissed
    return JsonResponse({'success': True})


# ===================================================================
#  پنل مدیریت — اعلان‌ها
# ===================================================================

@staff_member_required
def admin_dashboard(request):
    """داشبورد اطلاع‌رسانی"""
    announcements = Announcement.objects.all().order_by('order')
    sms_templates = SMSTemplate.objects.all()
    sms_logs = SMSLog.objects.all()[:20]

    # آمار
    sms_total = SMSLog.objects.count()
    sms_sent = SMSLog.objects.filter(status='sent').count()
    sms_failed = SMSLog.objects.filter(status='failed').count()

    context = {
        'announcements': announcements,
        'sms_templates': sms_templates,
        'sms_logs': sms_logs,
        'sms_total': sms_total,
        'sms_sent': sms_sent,
        'sms_failed': sms_failed,
    }
    return render(request, 'notifications/admin_dashboard.html', context)


# --- اعلان CRUD ---
@staff_member_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'اعلان ایجاد شد.')
            return redirect('notifications:admin_dashboard')
    else:
        form = AnnouncementForm()
    return render(request, 'notifications/announcement_form.html', {
        'form': form, 'title': 'ایجاد اعلان', 'is_edit': False
    })


@staff_member_required
def announcement_edit(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            form.save()
            messages.success(request, 'اعلان بروزرسانی شد.')
            return redirect('notifications:admin_dashboard')
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, 'notifications/announcement_form.html', {
        'form': form, 'announcement': ann, 'title': f'ویرایش اعلان', 'is_edit': True
    })


@staff_member_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'اعلان حذف شد.')
    return redirect('notifications:admin_dashboard')


# --- قالب پیامک CRUD ---
@staff_member_required
def sms_template_create(request):
    if request.method == 'POST':
        form = SMSTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'قالب پیامک ذخیره شد.')
            return redirect('notifications:admin_dashboard')
    else:
        form = SMSTemplateForm()
    return render(request, 'notifications/sms_template_form.html', {
        'form': form, 'title': 'افزودن قالب پیامک', 'is_edit': False
    })


@staff_member_required
def sms_template_edit(request, pk):
    tpl = get_object_or_404(SMSTemplate, pk=pk)
    if request.method == 'POST':
        form = SMSTemplateForm(request.POST, instance=tpl)
        if form.is_valid():
            form.save()
            messages.success(request, 'قالب بروزرسانی شد.')
            return redirect('notifications:admin_dashboard')
    else:
        form = SMSTemplateForm(instance=tpl)
    return render(request, 'notifications/sms_template_form.html', {
        'form': form, 'template_obj': tpl, 'title': f'ویرایش: {tpl.get_event_display()}', 'is_edit': True
    })


@staff_member_required
def sms_template_delete(request, pk):
    tpl = get_object_or_404(SMSTemplate, pk=pk)
    if request.method == 'POST':
        tpl.delete()
        messages.success(request, 'قالب حذف شد.')
    return redirect('notifications:admin_dashboard')


@staff_member_required
def sms_log_list(request):
    """لاگ کامل پیامک‌ها"""
    logs = SMSLog.objects.all()
    status = request.GET.get('status', '')
    if status:
        logs = logs.filter(status=status)
    return render(request, 'notifications/sms_log_list.html', {'logs': logs[:100], 'current_status': status})
