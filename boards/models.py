from django.db import models
from django.conf import settings
from django.urls import reverse


class Board(models.Model):
    """Model representing a board (collection of pins)"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'title']
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('boards:detail', kwargs={'pk': self.pk})
    
    @property
    def pin_count(self):
        """Return the number of pins in this board"""
        return self.pins.count()
