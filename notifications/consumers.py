import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room_group_name = f'notifications_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current unread count
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'mark_read':
            notification_id = data.get('notification_id')
            await self.mark_notification_read(notification_id)
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': count
            }))
        
        elif action == 'mark_all_read':
            await self.mark_all_read()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': 0
            }))
    
    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification'],
            'count': event['count']
        }))
    
    async def send_notification(self, event):
        # Send message notification (from chat) to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['notification']['type'],
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        return self.user.notifications.filter(is_read=False).count()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = self.user.notifications.get(id=notification_id)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_all_read(self):
        self.user.notifications.filter(is_read=False).update(is_read=True)
