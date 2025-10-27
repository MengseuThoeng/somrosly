import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Check if user is participant of this room
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark messages as read
        await self.mark_messages_read()
    
    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return
        
        # Save message to database
        message = await self.save_message(message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message['id'],
                    'content': message['content'],
                    'sender': message['sender'],
                    'sender_id': message['sender_id'],
                    'created_at': message['created_at'],
                }
            }
        )
        
        # Send notification to recipient
        recipient_id = await self.get_recipient_id()
        if recipient_id:
            await self.channel_layer.group_send(
                f'notifications_{recipient_id}',
                {
                    'type': 'send_notification',
                    'notification': {
                        'type': 'new_message',
                        'message': f'{message["sender"]}: {message_content[:50]}',
                        'sender': message['sender'],
                        'link': f'/chat/{message["sender"]}/',
                        'unread_count': await self.get_unread_count_for_user(recipient_id)
                    }
                }
            )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
        
        # Mark as read if not own message
        if event['message']['sender_id'] != self.user.id:
            await self.mark_messages_read()
    
    @database_sync_to_async
    def check_participant(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        
        # Update room timestamp
        room.save()
        
        return {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'created_at': message.created_at.strftime('%H:%M')
        }
    
    @database_sync_to_async
    def mark_messages_read(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            room.messages.filter(is_read=False).exclude(sender=self.user).update(is_read=True)
        except ChatRoom.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_recipient_id(self):
        """Get the other participant's ID in this chat room"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            other_user = room.participants.exclude(id=self.user.id).first()
            return other_user.id if other_user else None
        except ChatRoom.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_unread_count_for_user(self, user_id):
        """Get unread message count for a specific user"""
        from users.models import User
        try:
            user = User.objects.get(id=user_id)
            user_rooms = ChatRoom.objects.filter(participants=user)
            unread_count = Message.objects.filter(
                room__in=user_rooms,
                is_read=False
            ).exclude(sender=user).count()
            return unread_count
        except User.DoesNotExist:
            return 0
