from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from PIL import Image
import random


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    email = models.EmailField(max_length=191, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_premium = models.BooleanField(default=False)
    
    # Email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Social media links
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def generate_verification_token(self):
        """Generate a unique verification token"""
        self.email_verification_token = get_random_string(64)
        self.save(update_fields=['email_verification_token'])
        return self.email_verification_token
    
    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username


class PasswordResetToken(models.Model):
    """Model for password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
    
    def is_valid(self):
        """Check if token is still valid (24 hours)"""
        return not self.is_used and self.created_at > timezone.now() - timedelta(hours=24)
    
    @classmethod
    def create_token(cls, user):
        """Create a new password reset token"""
        token = get_random_string(64)
        return cls.objects.create(user=user, token=token)


class EmailOTP(models.Model):
    """Model for email OTP verification"""
    email = models.EmailField(max_length=191)
    otp = models.CharField(max_length=6)
    user_data = models.JSONField()  # Store registration data temporarily
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def is_valid(self):
        """Check if OTP is still valid (10 minutes) and not exceeded attempts"""
        return (
            not self.is_verified and
            self.attempts < 5 and
            self.created_at > timezone.now() - timedelta(minutes=10)
        )
    
    @classmethod
    def generate_otp(cls, email, user_data):
        """Generate a new 6-digit OTP"""
        # Delete old OTPs for this email
        cls.objects.filter(email=email, is_verified=False).delete()
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        return cls.objects.create(email=email, otp=otp, user_data=user_data)
