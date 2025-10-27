from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import User, PasswordResetToken, EmailOTP
from .forms import (UserRegistrationForm, UserLoginForm, UserUpdateForm, 
                   PasswordResetRequestForm, PasswordResetForm)


def register(request):
    """User registration view with OTP verification"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Don't create user yet, store data and send OTP
            email = form.cleaned_data['email']
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'users/register.html', {'form': form})
            
            # Store form data in session
            user_data = {
                'username': form.cleaned_data['username'],
                'email': email,
                'password': form.cleaned_data['password1'],
                'first_name': form.cleaned_data.get('first_name', ''),
                'last_name': form.cleaned_data.get('last_name', ''),
            }
            
            # Generate OTP
            otp_instance = EmailOTP.generate_otp(email, user_data)
            
            print("=" * 50)
            print(f"🔐 OTP GENERATED FOR: {email}")
            print(f"📧 VERIFICATION CODE: {otp_instance.otp}")
            print(f"⏰ EXPIRES IN: 10 minutes")
            print("=" * 50)
            
            # Send OTP email
            try:
                send_mail(
                    subject='Your Somrosly Verification Code',
                    message=f'''Welcome to Somrosly!

Your verification code is: {otp_instance.otp}

This code will expire in 10 minutes.
Do not share this code with anyone.

If you didn't request this code, please ignore this email.

Thanks,
The Somrosly Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f'✅ Verification code sent to {email}! Check your email and enter the 6-digit code.')
                # Redirect to OTP verification page
                return redirect('users:verify_otp', email=email)
            except Exception as e:
                print(f"Email error: {e}")
                messages.error(request, f'Failed to send verification code. Please try again.')
                return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def verify_otp(request, email):
    """Verify OTP and create user account"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    # Decode email if needed (handle URL encoding)
    from urllib.parse import unquote
    email = unquote(email)
    
    # Get the latest OTP for this email
    try:
        otp_instance = EmailOTP.objects.filter(email=email, is_verified=False).latest('created_at')
        print(f"Found OTP for {email}: {otp_instance.otp}")  # Debug
    except EmailOTP.DoesNotExist:
        print(f"No OTP found for email: {email}")  # Debug
        print(f"All OTPs in DB: {[(o.email, o.otp, o.is_verified) for o in EmailOTP.objects.all()]}")  # Debug
        messages.error(request, f'No verification code found for {email}. Please register again.')
        return redirect('users:register')
    
    # Check if OTP is still valid
    if not otp_instance.is_valid():
        messages.error(request, 'Verification code expired or too many attempts. Please register again.')
        return redirect('users:register')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        
        print(f"Entered OTP: {entered_otp}, Expected: {otp_instance.otp}")  # Debug
        
        # Increment attempts
        otp_instance.attempts += 1
        otp_instance.save()
        
        if entered_otp == otp_instance.otp:
            # OTP is correct, create the user
            user_data = otp_instance.user_data
            
            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                )
                user.is_email_verified = True
                user.is_active = True
                user.save()
                
                # Mark OTP as verified
                otp_instance.is_verified = True
                otp_instance.save()
                
                # Auto login the user
                login(request, user)
                messages.success(request, f'Welcome to Somrosly, {user.username}! Your account has been created successfully.')
                return redirect('core:home')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'users/verify_otp.html', {'email': email})
        else:
            remaining_attempts = 5 - otp_instance.attempts
            if remaining_attempts > 0:
                messages.error(request, f'Invalid verification code. {remaining_attempts} attempts remaining.')
            else:
                messages.error(request, 'Too many failed attempts. Please register again.')
                return redirect('users:register')
    
    return render(request, 'users/verify_otp.html', {'email': email})


def resend_otp(request, email):
    """Resend OTP to email"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    # Decode email if needed
    from urllib.parse import unquote
    email = unquote(email)
    
    try:
        # Get the latest OTP
        old_otp = EmailOTP.objects.filter(email=email).latest('created_at')
        user_data = old_otp.user_data
        
        # Generate new OTP
        otp_instance = EmailOTP.generate_otp(email, user_data)
        
        print(f"Resending OTP to {email}: {otp_instance.otp}")  # Debug
        
        # Send OTP email
        try:
            send_mail(
                subject='Your New Somrosly Verification Code',
                message=f'''Welcome to Somrosly!

Your new verification code is: {otp_instance.otp}

This code will expire in 10 minutes.
Do not share this code with anyone.

Thanks,
The Somrosly Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, f'A new verification code has been sent to {email}.')
        except Exception as e:
            messages.error(request, 'Failed to send verification code. Please try again.')
    except EmailOTP.DoesNotExist:
        messages.error(request, 'No verification request found. Please register again.')
        return redirect('users:register')
    
    return redirect('users:verify_otp', email=email)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user is active (email verified)
                if not user.is_active:
                    messages.error(request, 'Please verify your email address before logging in. Check your inbox for the verification link.')
                    return render(request, 'users/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile(request, username=None):
    """User profile view"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get user's boards and pins count
    boards_count = user.boards.count() if hasattr(user, 'boards') else 0
    pins_count = user.pins.count() if hasattr(user, 'pins') else 0
    
    context = {
        'profile_user': user,
        'boards_count': boards_count,
        'pins_count': pins_count,
        'is_own_profile': request.user == user,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile view"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


def verify_email(request, token):
    """Email verification view"""
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.is_active = True  # Activate the account
        user.email_verification_token = ''
        user.save()
        messages.success(request, 'Your email has been verified successfully! You can now log in.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
    
    return redirect('users:login')


def password_reset_request(request):
    """Password reset request view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                reset_token = PasswordResetToken.create_token(user)
                
                # Send password reset email
                reset_url = request.build_absolute_uri(
                    reverse('users:password_reset', args=[reset_token.token])
                )
                
                send_mail(
                    subject='Reset your Somrosly password',
                    message=f'''Hi {user.username},

We received a request to reset your password for your Somrosly account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request a password reset, please ignore this email.

Thanks,
The Somrosly Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset instructions have been sent to your email.')
                return redirect('users:login')
            except User.DoesNotExist:
                messages.success(request, 'If an account exists with that email, password reset instructions have been sent.')
                return redirect('users:login')
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again later.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset(request, token):
    """Password reset view"""
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or has already been used.')
        return redirect('users:password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'Your password has been reset successfully! You can now log in.')
            return redirect('users:login')
    else:
        form = PasswordResetForm()
    
    return render(request, 'users/password_reset.html', {'form': form, 'token': token})
