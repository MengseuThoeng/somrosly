from django.db import models
from django.conf import settings
from django.urls import reverse
from PIL import Image


class Pin(models.Model):
    """Model representing a pin (image/idea)"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pins'
    )
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='pins',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='pins/')
    source_url = models.URLField(max_length=500, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_pins',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('pins:detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        """Override save to optimize images"""
        super().save(*args, **kwargs)
        
        if self.image:
            try:
                img = Image.open(self.image.path)
                
                # Resize if too large
                max_size = (1200, 1200)
                if img.height > max_size[1] or img.width > max_size[0]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, optimize=True, quality=85)
            except Exception:
                pass
    
    @property
    def like_count(self):
        """Return the number of likes"""
        return self.likes.count()
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    @property
    def comment_count(self):
        """Return the number of comments"""
        return self.comments.count()


class Comment(models.Model):
    """Model representing a comment on a pin"""
    
    pin = models.ForeignKey(
        Pin,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        help_text='Parent comment for nested replies'
    )
    text = models.TextField(max_length=1000)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.pin.title}"
    
    @property
    def like_count(self):
        """Return the number of likes"""
        return self.likes.count()
    
    @property
    def reply_count(self):
        """Return the number of replies"""
        return self.replies.count()
