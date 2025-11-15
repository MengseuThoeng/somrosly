# 🔑 How to Get PayPal API Keys - Step by Step Guide

## 📋 Prerequisites
- A PayPal account (personal or business)
- Email access for verification

---

## 🚀 Step-by-Step Instructions

### Step 1: Go to PayPal Developer Website
1. Open your browser
2. Go to: **https://developer.paypal.com/**
3. Click **"Log In"** in the top right corner

![PayPal Developer Homepage](https://developer.paypal.com/)

---

### Step 2: Sign In with PayPal
1. Enter your PayPal email and password
2. Click **"Log In"**
3. Complete 2-factor authentication if prompted
4. You'll be redirected to the Developer Dashboard

**Note:** If you don't have a PayPal account:
- Click **"Sign Up"** 
- Create a free PayPal account first
- Then return to developer.paypal.com

---

### Step 3: Navigate to My Apps & Credentials
1. Once logged in, look at the left sidebar
2. Click on **"My Apps & Credentials"**
3. You'll see two tabs at the top:
   - **Sandbox** (for testing)
   - **Live** (for real payments)

**Start with Sandbox for testing!**

---

### Step 4: Create a New App (Sandbox Mode)
1. Make sure you're on the **"Sandbox"** tab
2. Scroll down to **"REST API apps"** section
3. Click the **"Create App"** button

---

### Step 5: Fill in App Details
1. **App Name:** Enter `Somrosly Premium` (or any name you prefer)
2. **Sandbox Business Account:** 
   - If you see a dropdown, select the default sandbox account
   - If empty, one will be created automatically
3. Click **"Create App"** button

---

### Step 6: Get Your Sandbox API Credentials

After creating the app, you'll see your credentials:

**Client ID (Sandbox)**
```
AeXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
- This is visible immediately
- Copy this entire string

**Secret (Sandbox)**
- Click **"Show"** button next to Secret
- Copy the revealed secret key
```
ENxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Step 7: Add to Your .env File

1. Open your `.env` file in the Somrosly project
2. Add these lines (replace with your actual keys):

```env
# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AeXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PAYPAL_CLIENT_SECRET=ENxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

3. Save the file

---

### Step 8: Create Sandbox Test Accounts

To test payments, you need test buyer and seller accounts:

1. In the left sidebar, click **"Sandbox"** → **"Accounts"**
2. You'll see default test accounts created:
   - **Business Account** (receives payments)
   - **Personal Account** (makes payments)

**To see login credentials:**
1. Click the **"..."** menu on any account
2. Click **"View/Edit Account"**
3. You'll see:
   - Email address
   - Password (or System Generated Password)
4. **Write these down for testing!**

---

### Step 9: Test Your Integration

1. Start your Django server:
```bash
python manage.py runserver
```

2. Go to: **http://127.0.0.1:8000/payments/premium/**

3. Click **"Pay with PayPal"** button

4. You'll be redirected to PayPal Sandbox

5. Log in with your **Personal (Buyer) Test Account**:
   - Email: `sb-xxxxx@personal.example.com`
   - Password: `xxxxxxxxx`

6. Approve the $2.00 payment

7. You'll be redirected back to Somrosly

8. Your account should now be Premium! ✅

---

## 🌐 For Production (Real Payments)

**⚠️ Only do this when ready to accept real money!**

### Get Live API Credentials:

1. Go back to **"My Apps & Credentials"**
2. Click the **"Live"** tab (not Sandbox)
3. Scroll to **"REST API apps"**
4. Click **"Create App"**
5. Enter app name: `Somrosly Premium Live`
6. Click **"Create App"**
7. Copy your **Live Client ID** and **Secret**

### Update .env for Production:

```env
# PayPal Configuration - PRODUCTION
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=your-live-client-id-here
PAYPAL_CLIENT_SECRET=your-live-secret-here
```

**Important:** 
- Live mode processes **real money**
- Test thoroughly in sandbox first!
- Keep your live secret key secure

---

## 📸 Visual Reference

### Where to Find Everything:

```
developer.paypal.com
├── Login (top right)
├── Dashboard
│   ├── My Apps & Credentials (left sidebar)
│   │   ├── Sandbox Tab
│   │   │   ├── Create App
│   │   │   ├── Client ID (visible)
│   │   │   └── Secret (click Show)
│   │   └── Live Tab
│   │       ├── Create App
│   │       ├── Client ID
│   │       └── Secret
│   └── Sandbox → Accounts (left sidebar)
│       ├── Business Account
│       └── Personal Account (for testing)
```

---

## 🧪 Testing Checklist

Before going live, test these scenarios:

- ✅ Click "Pay with PayPal" button
- ✅ Successfully log in to PayPal sandbox
- ✅ Approve payment
- ✅ Redirect back to app
- ✅ User upgraded to premium
- ✅ Success message displayed
- ✅ Premium badge shows on profile
- ✅ Can access premium pins

---

## ❓ Troubleshooting

### "Invalid credentials" error?
- Double-check your Client ID and Secret in `.env`
- Make sure there are no extra spaces
- Verify `PAYPAL_MODE=sandbox` matches your credentials type

### PayPal login page doesn't load?
- Check your internet connection
- Verify the app is created in PayPal dashboard
- Check Django logs for errors

### Payment approved but user not upgraded?
- Check Django server logs
- Verify the return URL is accessible
- Make sure session is maintained

### Can't find "Create App" button?
- Make sure you're logged in
- Verify email is confirmed
- Try refreshing the page

---

## 📞 Need Help?

- **PayPal Developer Support:** https://developer.paypal.com/support/
- **PayPal Developer Docs:** https://developer.paypal.com/docs/
- **Sandbox Testing Guide:** https://developer.paypal.com/docs/api-basics/sandbox/

---

## 🎯 Quick Summary

1. **Go to:** https://developer.paypal.com/
2. **Log in** with your PayPal account
3. **Navigate to:** My Apps & Credentials → Sandbox
4. **Click:** Create App
5. **Name it:** Somrosly Premium
6. **Copy:** Client ID and Secret
7. **Add to** `.env` file:
   ```env
   PAYPAL_MODE=sandbox
   PAYPAL_CLIENT_ID=your-client-id
   PAYPAL_CLIENT_SECRET=your-secret
   ```
8. **Test** at http://127.0.0.1:8000/payments/premium/

---

**That's it! You're ready to accept PayPal payments! 🎉**
