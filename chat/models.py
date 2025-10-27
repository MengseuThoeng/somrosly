from django.db import models
from django.conf import settings


class Friendship(models.Model):
    """Model for friend relationships"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    )
    
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            models.Q(from_user=user1, to_user=user2, status='accepted') |
            models.Q(from_user=user2, to_user=user1, status='accepted')
        ).exists()
    
    @classmethod
    def get_friends(cls, user):
        """Get all friends of a user"""
        friend_ids = cls.objects.filter(
            models.Q(from_user=user, status='accepted') |
            models.Q(to_user=user, status='accepted')
        ).values_list('from_user', 'to_user')
        
        # Flatten and remove self
        friends_ids = set()
        for from_id, to_id in friend_ids:
            friends_ids.add(from_id if from_id != user.id else to_id)
        
        from users.models import User
        return User.objects.filter(id__in=friends_ids)


class ChatRoom(models.Model):
    """Model for private chat rooms between friends"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        users = list(self.participants.all()[:2])
        if len(users) == 2:
            return f"Chat: {users[0].username} & {users[1].username}"
        return f"ChatRoom #{self.id}"
    
    @property
    def last_message(self):
        return self.messages.first()
    
    @classmethod
    def get_or_create_room(cls, user1, user2):
        """Get or create a chat room between two users"""
        # Check if room already exists
        room = cls.objects.filter(participants=user1).filter(participants=user2).first()
        
        if not room:
            room = cls.objects.create()
            room.participants.add(user1, user2)
        
        return room


class Message(models.Model):
    """Model for chat messages"""
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
