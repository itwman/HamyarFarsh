"""
فاز 21: ویوهای چت آنلاین و تیکت پشتیبانی
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ChatSession, ChatMessage, Ticket, TicketReply
from .forms import ChatStartForm, TicketForm, TicketReplyForm, AdminReplyForm


# ===================================================================
#  چت آنلاین — ویجت فوتر (AJAX)
# ===================================================================

@require_POST
def chat_start(request):
    """شروع چت جدید — AJAX"""
    form = ChatStartForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'message': 'اطلاعات را کامل وارد کنید.'})

    session = ChatSession.objects.create(
        visitor_name=form.cleaned_data['name'],
        visitor_phone=form.cleaned_data.get('phone', ''),
        user=request.user if request.user.is_authenticated else None,
        page_url=request.POST.get('page_url', ''),
        ip_address=_get_ip(request),
    )
    ChatMessage.objects.create(
        session=session,
        message=form.cleaned_data['message'],
        is_admin=False,
    )

    request.session['chat_session_key'] = str(session.session_key)

    # اطلاع‌رسانی به مدیر
    _notify_admin_new_chat(session)

    return JsonResponse({
        'success': True,
        'session_key': str(session.session_key),
        'message': 'پیام شما ارسال شد. به‌زودی پاسخ می‌دهیم.',
    })


@require_POST
def chat_send(request):
    """ارسال پیام در چت — AJAX"""
    session_key = request.POST.get('session_key') or request.session.get('chat_session_key')
    msg = request.POST.get('message', '').strip()

    if not session_key or not msg:
        return JsonResponse({'success': False})

    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'سشن چت یافت نشد.'})

    ChatMessage.objects.create(session=session, message=msg, is_admin=False)
    session.status = 'open'
    session.save(update_fields=['status', 'updated_at'])

    return JsonResponse({'success': True})


def chat_messages(request):
    """دریافت پیام‌های چت — AJAX polling"""
    session_key = request.GET.get('session_key') or request.session.get('chat_session_key')
    if not session_key:
        return JsonResponse({'messages': []})

    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'messages': []})

    msgs = session.messages.order_by('created_at')
    # خوانده شدن پیام‌های مدیر
    msgs.filter(is_admin=True, is_read=False).update(is_read=True)

    data = [{
        'message': m.message,
        'is_admin': m.is_admin,
        'time': m.jalali_time,
        'is_read': m.is_read,
    } for m in msgs]

    return JsonResponse({'messages': data, 'status': session.status})


# ===================================================================
#  پنل مدیریت چت
# ===================================================================

@staff_member_required
def admin_chat_list(request):
    """لیست چت‌ها"""
    sessions = ChatSession.objects.all()
    status = request.GET.get('status', '')
    if status:
        sessions = sessions.filter(status=status)

    open_count = ChatSession.objects.filter(status='open').count()
    total = ChatSession.objects.count()

    context = {
        'sessions': sessions[:50],
        'open_count': open_count,
        'total': total,
        'current_status': status,
    }
    return render(request, 'live_chat/admin_chat_list.html', context)


@staff_member_required
def admin_chat_detail(request, pk):
    """پاسخگویی به چت"""
    session = get_object_or_404(ChatSession, pk=pk)
    msgs = session.messages.order_by('created_at')

    # خوانده شدن پیام‌های بازدیدکننده
    msgs.filter(is_admin=False, is_read=False).update(is_read=True)

    if request.method == 'POST':
        msg = request.POST.get('message', '').strip()
        if msg:
            ChatMessage.objects.create(
                session=session, message=msg,
                is_admin=True, admin_user=request.user
            )
            session.status = 'answered'
            session.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'پاسخ ارسال شد.')
            return redirect('live_chat:admin_chat_detail', pk=pk)

    context = {'session': session, 'messages_list': msgs}
    return render(request, 'live_chat/admin_chat_detail.html', context)


@staff_member_required
def admin_chat_close(request, pk):
    session = get_object_or_404(ChatSession, pk=pk)
    session.status = 'closed'
    session.save(update_fields=['status'])
    messages.success(request, 'چت بسته شد.')
    return redirect('live_chat:admin_chat_list')


# ===================================================================
#  تیکت پشتیبانی — پنل مشتری
# ===================================================================

@login_required
def ticket_list(request):
    """لیست تیکت‌های مشتری"""
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'live_chat/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_create(request):
    """ایجاد تیکت"""
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            TicketReply.objects.create(
                ticket=ticket, user=request.user,
                message=form.cleaned_data['message'], is_admin=False
            )
            messages.success(request, f'تیکت #{ticket.pk} ایجاد شد.')
            return redirect('live_chat:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm(user=request.user)
    return render(request, 'live_chat/ticket_form.html', {
        'form': form, 'title': 'ایجاد تیکت پشتیبانی'
    })


@login_required
def ticket_detail(request, pk):
    """مشاهده و پاسخ تیکت"""
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    replies = ticket.replies.order_by('created_at')

    if request.method == 'POST' and ticket.status != 'closed':
        form = TicketReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = TicketReply.objects.create(
                ticket=ticket, user=request.user,
                message=form.cleaned_data['message'],
                attachment=form.cleaned_data.get('attachment'),
                is_admin=False
            )
            ticket.status = 'open'
            ticket.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'پاسخ ارسال شد.')
            return redirect('live_chat:ticket_detail', pk=pk)
    else:
        form = TicketReplyForm()

    context = {'ticket': ticket, 'replies': replies, 'form': form}
    return render(request, 'live_chat/ticket_detail.html', context)


# ===================================================================
#  تیکت — پنل مدیریت
# ===================================================================

@staff_member_required
def admin_ticket_list(request):
    """لیست تیکت‌ها — مدیریت"""
    tickets = Ticket.objects.select_related('user').all()
    status = request.GET.get('status', '')
    if status:
        tickets = tickets.filter(status=status)

    open_count = Ticket.objects.filter(status__in=['open', 'in_progress']).count()

    context = {
        'tickets': tickets[:50],
        'open_count': open_count,
        'current_status': status,
    }
    return render(request, 'live_chat/admin_ticket_list.html', context)


@staff_member_required
def admin_ticket_detail(request, pk):
    """پاسخ مدیر به تیکت"""
    ticket = get_object_or_404(Ticket, pk=pk)
    replies = ticket.replies.order_by('created_at')

    if request.method == 'POST':
        form = AdminReplyForm(request.POST)
        if form.is_valid():
            TicketReply.objects.create(
                ticket=ticket, user=request.user,
                message=form.cleaned_data['message'], is_admin=True
            )
            ticket.status = form.cleaned_data['status']
            ticket.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'پاسخ ارسال شد.')
            return redirect('live_chat:admin_ticket_detail', pk=pk)
    else:
        form = AdminReplyForm(initial={'status': ticket.status})

    context = {'ticket': ticket, 'replies': replies, 'form': form}
    return render(request, 'live_chat/admin_ticket_detail.html', context)


# ===================================================================
#  Helpers
# ===================================================================

def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0] if x else request.META.get('REMOTE_ADDR')


def _notify_admin_new_chat(session):
    """اطلاع‌رسانی پیام جدید چت به مدیر"""
    try:
        from notifications.services import send_sms
        from settings_app.models import SiteSettings
        ss = SiteSettings.get_solo()
        if ss.mobile:
            send_sms(ss.mobile, f'پیام چت جدید از {session.visitor_name} ({session.visitor_phone})',
                     event='new_chat')
    except Exception:
        pass
