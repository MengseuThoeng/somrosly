# 📌 Somrosly - Premium Pinterest Clone

A modern, feature-rich Pinterest-style social media platform with premium subscriptions, real-time chat, and cloud storage integration.

![Django](https://img.shields.io/badge/Django-5.1.13-green)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 🎨 Core Features
- **Pin Management**: Create, edit, delete, and organize pins
- **Boards**: Create and manage custom boards
- **Discovery Feed**: Personalized home feed with latest pins
- **Search**: Advanced search functionality for pins and users
- **User Profiles**: Customizable profiles with profile pictures
- **Following System**: Follow/unfollow users and see their content
- **Likes & Saves**: Interact with pins and save to boards

### 💬 Social Features
- **Real-time Chat**: WebSocket-based instant messaging
- **Friends System**: Add friends and manage friend requests
- **Notifications**: Real-time notifications for interactions
- **Comments**: Comment system on pins (nested replies supported)

### 👑 Premium Features
- **Premium Membership**: $2/month subscription
- **Premium-Only Pins**: Create exclusive content for premium users
- **Premium Badge**: Gold crown badge on profiles
- **Ad-Free Experience**: Browse without interruptions
- **Priority Support**: Get help faster

### 💳 Payment Integration
- **Stripe**: Credit/Debit card payments with recurring subscriptions
- **PayPal**: PayPal recurring subscriptions
- **Secure**: PCI-compliant payment processing
- **Auto-Renewal**: Automatic monthly billing

### ☁️ Cloud Storage
- **MinIO Integration**: Scalable object storage for media files
- **Image Optimization**: Automatic image processing
- **CDN Support**: Fast media delivery

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MySQL 8.0+
- MinIO (for cloud storage)
- Stripe Account (for payments)
- PayPal Account (for payments)

### 1. Clone Repository
```bash
git clone https://github.com/MengseuThoeng/somrosly.git
cd somrosly
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=somrosly_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
STRIPE_PRICE_ID=your-price-id

# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret
PAYPAL_PLAN_ID=your-paypal-plan-id

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@somrosly.com

# MinIO/S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=your-minio-access-key
AWS_SECRET_ACCESS_KEY=your-minio-secret-key
AWS_STORAGE_BUCKET_NAME=somrosly-media
AWS_S3_ENDPOINT_URL=http://your-server-ip:9000
AWS_S3_REGION_NAME=us-east-1
AWS_S3_USE_SSL=False
AWS_S3_VERIFY=False
```

### 5. Create Database
```bash
mysql -u root -p
CREATE DATABASE somrosly_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 9. Run Development Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 📦 Project Structure

```
somrosly/
├── boards/              # Board management
├── chat/                # Real-time chat system
├── core/                # Core functionality (home, search)
├── notifications/       # Notification system
├── payments/            # Stripe & PayPal integration
├── pins/                # Pin management
├── users/               # User authentication & profiles
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploaded files (local)
├── somrosly_project/    # Project settings
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Technologies Used

### Backend
- **Django 5.1.13**: Web framework
- **Django Channels**: WebSocket support for real-time features
- **Django REST Framework**: API endpoints
- **Daphne**: ASGI server
- **PyMySQL**: MySQL database adapter

### Frontend
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: Interactive UI components
- **WebSocket**: Real-time communication
- **Font Awesome**: Icons

### Storage & Media
- **MinIO**: S3-compatible object storage
- **Django Storages**: Cloud storage integration
- **Boto3**: AWS SDK for Python

### Payment Processing
- **Stripe**: Card payment processing
- **PayPal REST SDK**: PayPal subscriptions

### Database
- **MySQL**: Primary database

---

## 💳 Payment Setup

### Stripe Setup
1. Create account at https://stripe.com/
2. Get API keys from Dashboard
3. Create product and price in Stripe Dashboard
4. Add keys to `.env` file

**Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`

### PayPal Setup
1. Create developer account at https://developer.paypal.com/
2. Create REST API app
3. Run plan creation script:
```bash
python create_paypal_plan.py
```
4. Add credentials to `.env` file

**Sandbox Testing:**
- Use PayPal sandbox accounts
- Test mode - no real charges

---

## 🎨 Screenshots

### Home Feed
Modern Pinterest-style masonry layout with infinite scroll

### Premium Page
Beautiful gradient design with dual payment options (Stripe & PayPal)

### Chat System
Real-time messaging with friends list and online status

### Profile
User profiles with premium badge, follower counts, and pin collection

---

## 📝 API Documentation

### Authentication
- `POST /users/login/` - User login
- `POST /users/register/` - User registration
- `GET /users/logout/` - User logout

### Pins
- `GET /pins/` - List all pins
- `POST /pins/create/` - Create pin
- `GET /pins/<id>/` - Pin detail
- `POST /pins/<id>/like/` - Like pin
- `POST /pins/<id>/comment/` - Add comment

### Payments
- `GET /payments/premium/` - Premium page
- `POST /payments/create-checkout-session/` - Stripe checkout
- `POST /payments/paypal/create/` - PayPal subscription
- `POST /payments/cancel-subscription/` - Cancel subscription

---

## 🔧 Development

### Run Tests
```bash
python manage.py test
```

### Check Code Quality
```bash
python manage.py check
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Admin User
```bash
python manage.py createsuperuser
```

### Manual Premium Upgrade
```bash
python manage.py make_premium user@email.com
```

---

## 🚢 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use production database
- [ ] Set up HTTPS
- [ ] Configure static files serving
- [ ] Set up MinIO/S3 for media
- [ ] Configure email backend
- [ ] Set Stripe/PayPal to live mode
- [ ] Set up webhooks for payments
- [ ] Configure domain name
- [ ] Set up SSL certificates

### Environment Variables (Production)
- Change `PAYPAL_MODE` to `live`
- Use production Stripe keys
- Use production PayPal credentials
- Set strong `SECRET_KEY`
- Configure production database
- Enable `USE_S3=True`

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Contributors

- **Mengseu Thoeng** - [@MengseuThoeng](https://github.com/MengseuThoeng)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

For support, email mengseu2004@gmail.com or open an issue on GitHub.

---

## 🙏 Acknowledgments

- Inspired by Pinterest
- Built with Django
- Payment processing by Stripe & PayPal
- Cloud storage by MinIO
- Icons by Font Awesome

---

**⭐ Star this repo if you find it helpful!**
