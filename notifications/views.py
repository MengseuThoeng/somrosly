from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notifications_list(request):
    """List all notifications for the user"""
    notifications = request.user.notifications.all()[:50]
    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })


@login_required
def get_unread_count(request):
    """Get count of unread notifications"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_recent_notifications(request):
    """Get recent notifications for real-time updates"""
    notifications = request.user.notifications.filter(is_read=False)[:5]
    data = [{
        'id': notif.id,
        'type': notif.notification_type,
        'message': notif.message,
        'link': notif.link,
        'sender': notif.sender.username if notif.sender else None,
        'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for notif in notifications]
    
    return JsonResponse({
        'notifications': data,
        'count': request.user.notifications.filter(is_read=False).count()
    })


@login_required
def mark_as_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
