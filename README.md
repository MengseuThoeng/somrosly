# 🌸 Somrosly

**Somrosly** is a modern full-stack web application built with **Django** and **Stripe** integration.
Inspired by **Pinterest**, Somrosly provides a space for users to **discover**, **save**, and **share** visual inspirations within a clean and elegant interface.

Our mission is to build a creative community where users can curate ideas, express their imagination, and support creators through **secure Stripe payments**.

## 🧩 Tech Stack

* **Framework:** Django (Full Stack)
* **Frontend:** HTML, Tailwind CSS, JavaScript
* **Database:** MySQL
* **Payments:** Stripe API
* **Storage:** MinIO (S3-compatible)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- MySQL Server running on port 3306
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd Somrosly
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Create MySQL database**
```sql
CREATE DATABASE somrosly_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser!

---

## 💡 Features

* ✅ User registration and authentication
* ✅ Create, organize, and manage *boards* and *pins*
* ✅ Integrated Stripe payments for premium features and creator support
* ✅ Responsive, minimalist UI design
* ✅ Explore and search creative inspirations
* ✅ Image uploads and storage powered by MinIO

---

## 📁 Project Structure

```
Somrosly/
├── somrosly_project/        # Main project settings
├── users/                   # User authentication & profiles
├── boards/                  # Boards functionality
├── pins/                    # Pins functionality
├── payments/                # Stripe payment integration
├── core/                    # Core app (home, explore, search)
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploaded files
├── templates/               # HTML templates
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

---

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.
# somrosly
