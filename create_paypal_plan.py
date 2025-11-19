"""
PayPal Billing Plan Creator
This script creates a Product and Billing Plan for recurring subscriptions
"""

import requests
import json
from decouple import config

# PayPal Configuration
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET')

# PayPal API URLs
if PAYPAL_MODE == 'live':
    BASE_URL = 'https://api.paypal.com'
else:
    BASE_URL = 'https://api.sandbox.paypal.com'


def get_access_token():
    """Get PayPal OAuth access token"""
    url = f'{BASE_URL}/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Error getting access token: {response.text}")
        return None


def create_product(access_token):
    """Create a PayPal Product"""
    url = f'{BASE_URL}/v1/catalogs/products'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    
    product_data = {
        "name": "Somrosly Premium Membership",
        "description": "Premium membership with exclusive content access and ad-free experience",
        "type": "SERVICE",
        "category": "SOFTWARE",
        "image_url": "https://example.com/logo.png",  # Optional: Add your logo URL
        "home_url": "https://somrosly.com"  # Optional: Your website
    }
    
    response = requests.post(url, headers=headers, json=product_data)
    
    if response.status_code == 201:
        product = response.json()
        print(f"✅ Product created successfully!")
        print(f"Product ID: {product['id']}")
        print(f"Product Name: {product['name']}")
        return product['id']
    else:
        print(f"❌ Error creating product: {response.text}")
        return None


def create_billing_plan(access_token, product_id):
    """Create a PayPal Billing Plan"""
    url = f'{BASE_URL}/v1/billing/plans'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Prefer': 'return=representation'
    }
    
    plan_data = {
        "product_id": product_id,
        "name": "Somrosly Premium - Monthly",
        "description": "$2 per month premium subscription with automatic renewal",
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,  # 0 = unlimited until cancelled
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "2.00",
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee": {
                "value": "0.00",
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        },
        "taxes": {
            "percentage": "0",
            "inclusive": False
        }
    }
    
    response = requests.post(url, headers=headers, json=plan_data)
    
    if response.status_code == 201:
        plan = response.json()
        print(f"\n✅ Billing Plan created successfully!")
        print(f"Plan ID: {plan['id']}")
        print(f"Plan Name: {plan['name']}")
        print(f"Status: {plan['status']}")
        return plan['id']
    else:
        print(f"❌ Error creating billing plan: {response.text}")
        return None


def activate_plan(access_token, plan_id):
    """Activate the billing plan"""
    url = f'{BASE_URL}/v1/billing/plans/{plan_id}/activate'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 204:
        print(f"\n✅ Plan activated successfully!")
        return True
    else:
        print(f"❌ Error activating plan: {response.text}")
        return False


def main():
    print("=" * 60)
    print("PayPal Recurring Subscription Setup")
    print("=" * 60)
    print(f"Mode: {PAYPAL_MODE.upper()}")
    print(f"Client ID: {PAYPAL_CLIENT_ID[:20]}...")
    print("=" * 60)
    
    # Step 1: Get access token
    print("\n📡 Getting PayPal access token...")
    access_token = get_access_token()
    if not access_token:
        print("❌ Failed to get access token. Check your credentials.")
        return
    print("✅ Access token obtained")
    
    # Step 2: Create product
    print("\n📦 Creating PayPal Product...")
    product_id = create_product(access_token)
    if not product_id:
        print("❌ Failed to create product")
        return
    
    # Step 3: Create billing plan
    print("\n💳 Creating Billing Plan...")
    plan_id = create_billing_plan(access_token, product_id)
    if not plan_id:
        print("❌ Failed to create billing plan")
        return
    
    # Step 4: Activate plan
    print("\n🚀 Activating Plan...")
    if activate_plan(access_token, plan_id):
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your PayPal recurring subscription is ready!")
        print("=" * 60)
        print(f"\n📋 Add this to your .env file:")
        print(f"\nPAYPAL_PLAN_ID={plan_id}")
        print("\n" + "=" * 60)
    else:
        print("\n⚠️ Plan created but activation failed. You can activate it manually.")
        print(f"Plan ID: {plan_id}")
        print(f"\n📋 Add this to your .env file:")
        print(f"\nPAYPAL_PLAN_ID={plan_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("1. Your .env file has PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET")
        print("2. You have an active internet connection")
        print("3. Your PayPal credentials are correct")
