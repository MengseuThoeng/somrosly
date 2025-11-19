from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def premium(request):
    """Premium page view - shows upgrade options for non-premium users"""
    context = {
        'is_premium': request.user.is_premium,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/premium.html', context)


@login_required
@require_POST
def create_checkout_session(request):
    """Create a Stripe checkout session for premium subscription"""
    try:
        # Check if user is already premium
        if request.user.is_premium:
            return JsonResponse({'error': 'You are already a premium member'}, status=400)
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.build_absolute_uri('/payments/success/'),
            cancel_url=request.build_absolute_uri('/payments/premium/'),
            metadata={
                'user_id': request.user.id,
            }
        )
        
        return JsonResponse({'sessionId': checkout_session.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/success.html')


def payment_cancel(request):
    """Payment cancelled page"""
    return render(request, 'payments/cancel.html')


@login_required
@require_POST
def cancel_subscription(request):
    """Cancel premium subscription"""
    if request.user.is_premium:
        request.user.is_premium = False
        request.user.save()
        messages.success(request, 'Your premium subscription has been cancelled.')
    return redirect('payments:premium')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get user_id from metadata
        user_id = session.get('metadata', {}).get('user_id')
        
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(id=user_id)
                user.is_premium = True
                user.save()
                print(f"User {user.username} upgraded to premium!")
            except User.DoesNotExist:
                print(f"User with id {user_id} not found")
    
    # Handle subscription deleted (cancellation)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_email = subscription.get('customer_email')
        
        if customer_email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(email=customer_email)
                user.is_premium = False
                user.save()
                print(f"User {user.username} downgraded from premium")
            except User.DoesNotExist:
                print(f"User with email {customer_email} not found")
    
    return HttpResponse(status=200)


@login_required
@require_POST
def create_paypal_payment(request):
    """Create a PayPal subscription for premium membership"""
    try:
        # Check if user is already premium
        if request.user.is_premium:
            return JsonResponse({'error': 'You are already a premium member'}, status=400)
        
        # Get access token
        token_url = f"https://api{'.' if settings.PAYPAL_MODE == 'live' else '.sandbox.'}paypal.com/v1/oauth2/token"
        token_response = requests.post(
            token_url,
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
        )
        
        if token_response.status_code != 200:
            return JsonResponse({'error': 'Failed to get PayPal access token'}, status=400)
        
        access_token = token_response.json()['access_token']
        
        # Create subscription
        subscription_url = f"https://api{'.' if settings.PAYPAL_MODE == 'live' else '.sandbox.'}paypal.com/v1/billing/subscriptions"
        subscription_data = {
            "plan_id": settings.PAYPAL_PLAN_ID,
            "application_context": {
                "brand_name": "Somrosly",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": request.build_absolute_uri('/payments/paypal/execute/'),
                "cancel_url": request.build_absolute_uri('/payments/premium/')
            },
            "custom_id": str(request.user.id)  # Store user ID for later
        }
        
        subscription_response = requests.post(
            subscription_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            },
            json=subscription_data
        )
        
        if subscription_response.status_code == 201:
            subscription = subscription_response.json()
            # Get approval URL
            approval_url = next(
                (link['href'] for link in subscription.get('links', []) if link['rel'] == 'approve'),
                None
            )
            if approval_url:
                # Store subscription ID in session
                request.session['pending_paypal_subscription_id'] = subscription['id']
                return JsonResponse({'approval_url': approval_url})
            else:
                return JsonResponse({'error': 'No approval URL found'}, status=400)
        else:
            error_msg = subscription_response.json().get('message', 'Unknown error')
            return JsonResponse({'error': f'PayPal error: {error_msg}'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def execute_paypal_payment(request):
    """Execute PayPal subscription after user approval"""
    subscription_id = request.session.get('pending_paypal_subscription_id')
    
    if not subscription_id:
        messages.error(request, 'Invalid subscription session')
        return redirect('payments:premium')
    
    try:
        # Get access token
        token_url = f"https://api{'.' if settings.PAYPAL_MODE == 'live' else '.sandbox.'}paypal.com/v1/oauth2/token"
        token_response = requests.post(
            token_url,
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            data={'grant_type': 'client_credentials'},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
        )
        
        if token_response.status_code != 200:
            messages.error(request, 'Failed to verify PayPal subscription')
            return redirect('payments:premium')
        
        access_token = token_response.json()['access_token']
        
        # Get subscription details
        subscription_url = f"https://api{'.' if settings.PAYPAL_MODE == 'live' else '.sandbox.'}paypal.com/v1/billing/subscriptions/{subscription_id}"
        subscription_response = requests.get(
            subscription_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        if subscription_response.status_code == 200:
            subscription = subscription_response.json()
            
            # Check if subscription is active
            if subscription['status'] == 'ACTIVE':
                # Upgrade user to premium
                request.user.is_premium = True
                request.user.save()
                
                # Clear session
                request.session.pop('pending_paypal_subscription_id', None)
                
                messages.success(request, 'Payment successful! You are now a premium member.')
                return redirect('payments:payment_success')
            else:
                messages.error(request, f'Subscription status: {subscription["status"]}. Please try again.')
                return redirect('payments:premium')
        else:
            messages.error(request, 'Failed to verify subscription')
            return redirect('payments:premium')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('payments:premium')

