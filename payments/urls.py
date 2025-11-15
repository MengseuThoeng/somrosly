from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('premium/', views.premium, name='premium'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('paypal/create/', views.create_paypal_payment, name='create_paypal_payment'),
    path('paypal/execute/', views.execute_paypal_payment, name='execute_paypal_payment'),
]
