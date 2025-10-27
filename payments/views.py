from django.shortcuts import render


def premium(request):
    """Premium page view (placeholder for Stripe integration)"""
    return render(request, 'payments/premium.html')
