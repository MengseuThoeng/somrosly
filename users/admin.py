from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken, EmailOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_email_verified', 'is_premium', 'is_staff']
    list_filter = ['is_email_verified', 'is_premium', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'website', 'location', 'instagram', 'twitter')
        }),
        ('Email Verification', {
            'fields': ('is_email_verified', 'email_verification_token')
        }),
        ('Premium Status', {
            'fields': ('is_premium',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'bio')
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin configuration for password reset tokens"""
    list_display = ['user', 'token', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at']


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Admin configuration for email OTP"""
    list_display = ['email', 'otp', 'created_at', 'is_verified', 'attempts']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email', 'otp']
    readonly_fields = ['otp', 'created_at', 'user_data']
    
    def has_add_permission(self, request):
        """Disable manual creation of OTPs"""
        return False
