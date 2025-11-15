from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json
import paypalrestsdk

stripe.api_key = settings.STRIPE_SECRET_KEY

# Configure PayPal
paypalrestsdk.configure({
    "mode": getattr(settings, 'PAYPAL_MODE', 'sandbox'),  # sandbox or live
    "client_id": getattr(settings, 'PAYPAL_CLIENT_ID', ''),
    "client_secret": getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
})


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
    """Create a PayPal payment for premium subscription"""
    try:
        # Check if user is already premium
        if request.user.is_premium:
            return JsonResponse({'error': 'You are already a premium member'}, status=400)
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payments/paypal/execute/'),
                "cancel_url": request.build_absolute_uri('/payments/premium/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Somrosly Premium Subscription",
                        "sku": "premium-monthly",
                        "price": "2.00",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "2.00",
                    "currency": "USD"
                },
                "description": "Somrosly Premium Monthly Subscription - $2/month"
            }]
        })
        
        if payment.create():
            # Store user_id in session for later
            request.session['pending_premium_user_id'] = request.user.id
            
            # Get approval URL
            for link in payment.links:
                if link.rel == "approval_url":
                    return JsonResponse({'approval_url': str(link.href)})
        else:
            return JsonResponse({'error': payment.error}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def execute_paypal_payment(request):
    """Execute PayPal payment after user approval"""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, 'Invalid payment parameters')
        return redirect('payments:premium')
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Payment successful - upgrade user to premium
            user_id = request.session.get('pending_premium_user_id')
            
            if user_id and user_id == request.user.id:
                request.user.is_premium = True
                request.user.save()
                request.session.pop('pending_premium_user_id', None)
                messages.success(request, 'Payment successful! You are now a premium member.')
                return redirect('payments:payment_success')
            else:
                messages.error(request, 'User verification failed')
                return redirect('payments:premium')
        else:
            messages.error(request, f'Payment execution failed: {payment.error}')
            return redirect('payments:premium')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('payments:premium')

