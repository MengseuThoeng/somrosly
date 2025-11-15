# PayPal Integration Setup Guide

## Overview
Your Somrosly app now supports both **Stripe** and **PayPal** payment methods for premium subscriptions ($2/month).

## PayPal Setup Steps

### 1. Create PayPal Developer Account
1. Go to [PayPal Developer](https://developer.paypal.com/)
2. Sign up or log in with your PayPal account
3. Navigate to **Dashboard**

### 2. Create a REST API App
1. Go to **My Apps & Credentials**
2. Under **REST API apps**, click **Create App**
3. Enter app name: `Somrosly Premium`
4. Click **Create App**

### 3. Get Your Credentials

#### For Testing (Sandbox Mode):
1. In your app dashboard, you'll see:
   - **Sandbox Client ID** (starts with `A...`)
   - Click **Show** next to **Secret** to reveal it
2. Copy both credentials

#### For Production (Live Mode):
1. Toggle to **Live** tab in your app
2. Copy **Live Client ID** and **Secret**

### 4. Add Credentials to .env File

Add these lines to your `.env` file:

```env
# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your-sandbox-client-id-here
PAYPAL_CLIENT_SECRET=your-sandbox-secret-here
```

**For production**, change:
```env
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=your-live-client-id-here
PAYPAL_CLIENT_SECRET=your-live-secret-here
```

### 5. Test Your Integration

#### Sandbox Testing:
1. Use PayPal sandbox test accounts (found in PayPal Developer Dashboard)
2. Test buyer credentials:
   - Email: Generated in sandbox accounts section
   - Password: Generated password

#### Test the Flow:
1. Go to `http://127.0.0.1:8000/payments/premium/`
2. Click **Pay with PayPal** button
3. Log in with sandbox buyer account
4. Complete the payment
5. You'll be redirected back and upgraded to premium

## Payment Flow

### Stripe Flow:
1. User clicks "Pay with Stripe"
2. Redirected to Stripe Checkout
3. Enters card details
4. Payment processed
5. Webhook upgrades user to premium
6. Redirected to success page

### PayPal Flow:
1. User clicks "Pay with PayPal"
2. Redirected to PayPal
3. Logs in to PayPal account
4. Approves payment
5. Redirected back to app
6. Payment executed
7. User upgraded to premium
8. Shown success page

## Features Implemented

✅ Dual payment options (Stripe + PayPal)
✅ Secure payment processing
✅ Automatic premium upgrade
✅ Beautiful UI with both payment buttons
✅ Error handling
✅ Session management
✅ User verification

## PayPal Sandbox Test Accounts

To test PayPal:
1. Go to [PayPal Sandbox](https://www.sandbox.paypal.com/)
2. Log in with your developer account
3. Go to **Accounts** section
4. Create or use existing test accounts:
   - **Business Account** (seller) - receives payments
   - **Personal Account** (buyer) - makes payments

## Important Notes

⚠️ **Sandbox vs Live Mode**:
- `sandbox` = Testing with fake money
- `live` = Real payments with real money

⚠️ **Security**:
- Never commit `.env` file to git
- Keep your Client Secret secure
- Use environment variables in production

⚠️ **Payment Amount**:
- Currently set to $2.00 USD
- To change: Edit `payments/views.py` in `create_paypal_payment` function

## Troubleshooting

### PayPal button not working?
- Check `.env` has correct credentials
- Verify `PAYPAL_MODE` is set correctly
- Check browser console for errors

### Payment not upgrading user?
- Check Django logs for errors
- Verify session is maintained
- Ensure user is logged in

### Testing payments?
- Use sandbox mode for testing
- Don't use real PayPal credentials in sandbox
- Create test accounts in PayPal Developer Dashboard

## API Endpoints

- **Premium Page**: `/payments/premium/`
- **Create PayPal Payment**: `/payments/paypal/create/` (POST)
- **Execute Payment**: `/payments/paypal/execute/` (GET with params)
- **Success Page**: `/payments/success/`
- **Cancel Subscription**: `/payments/cancel-subscription/` (POST)

## Next Steps

1. Set up PayPal Developer account
2. Create REST API app
3. Add credentials to `.env`
4. Test with sandbox accounts
5. When ready for production, switch to `live` mode with live credentials

---

**Need Help?**
- PayPal Developer Docs: https://developer.paypal.com/docs/
- PayPal REST API Guide: https://developer.paypal.com/docs/api/overview/
