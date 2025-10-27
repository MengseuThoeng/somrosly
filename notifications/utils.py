from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification_to_user(user, notification):
    """Send real-time notification to user via WebSocket"""
    channel_layer = get_channel_layer()
    
    notification_data = {
        'id': notification.id,
        'type': notification.notification_type,
        'message': notification.message,
        'link': notification.link,
        'sender': notification.sender.username if notification.sender else None,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    unread_count = user.notifications.filter(is_read=False).count()
    
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'notification_message',
            'notification': notification_data,
            'count': unread_count
        }
    )
