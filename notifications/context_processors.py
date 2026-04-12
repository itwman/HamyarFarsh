"""Context processor برای نوار اعلان و شمارنده نوتیفیکیشن"""
from .models import Announcement, Notification


def notifications_context(request):
    # نوار اعلان فعال (فیلتر dismiss شده‌ها)
    announcements = list(Announcement.get_active())
    dismissed = request.session.get('dismissed_announcements', [])
    active_announcements = [a for a in announcements if a.id not in dismissed]

    # شمارنده نوتیفیکیشن
    unread_notif_count = 0
    if request.user.is_authenticated:
        unread_notif_count = Notification.unread_count(request.user)

    return {
        'active_announcements': active_announcements,
        'unread_notif_count': unread_notif_count,
    }
