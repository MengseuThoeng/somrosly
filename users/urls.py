from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<str:email>/', views.resend_otp, name='resend_otp'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<str:token>/', views.password_reset, name='password_reset'),
]
