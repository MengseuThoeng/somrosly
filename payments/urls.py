from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Will be implemented later with Stripe
    path('premium/', views.premium, name='premium'),
]
