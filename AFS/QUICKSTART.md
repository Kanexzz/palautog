# Faculty Scheduling System - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Clone & Setup Virtual Environment
```bash
cd d:/AFS
python -m venv venv
source venv/Scripts/activate  # Windows

# Or on Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Demo Data
```bash
python manage.py create_demo_data
```

### 5. Start Development Server
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 🔐 Demo Credentials

### Login Page (Auto-fill Button Available)
- **Username**: `admin`
- **Password**: `admin123`

---

## 📊 What You Get

### Landing Page
✅ Professional login interface matching CHMSU branding
✅ Green gradient background with university logo
✅ Demo account auto-fill button
✅ Responsive design for all devices

### Dashboard
✅ Welcome message
✅ Quick links to schedules and faculty
✅ User profile information
✅ Recent activity section

### Admin Panel
- Access: http://localhost:8000/admin
- Manage departments, courses, faculty, schedules
- User role management

---

## 🐳 Docker Setup (Alternative)

### Quick Start with Docker Compose
```bash
docker-compose up
```

This starts:
- Django web server (port 8000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Celery worker for async tasks

---

## 📁 Project Structure

```
AFS/
├── manage.py                 # Django CLI
├── requirements.txt          # Python packages
├── Dockerfile               # Container config
├── docker-compose.yml       # Multi-container setup
├── README.md               # Full documentation
│
├── config/                 # Main Django project
│   ├── settings.py        # Configuration (env-based)
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # Production server
│   └── celery.py          # Async task config
│
├── apps/
│   ├── core/              # Homepage & dashboard
│   ├── authentication/    # Login & user management
│   └── scheduling/        # Scheduling system
│
├── templates/             # HTML templates
│   ├── authentication/login.html
│   ├── core/dashboard.html
│   └── scheduling/schedule_*.html
│
└── static/               # CSS & JavaScript
    ├── css/style.css     # Custom styling
    └── js/main.js        # Client-side logic
```

---

## 🎨 Design Features

### Color Scheme
- **Primary Green**: #1f754a (CHMSU brand)
- **Accent Yellow**: #ffd700 (CHMSU brand)
- **Light Gray**: #f5f5f5 (Background)

### Responsive Breakpoints
- Desktop: ≥768px
- Tablet: 480px-768px
- Mobile: <480px

---

## 🔧 Management Commands

### Create Demo Data
```bash
python manage.py create_demo_data
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Run Tests
```bash
python manage.py test
```

---

## 📦 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Django 4.2, Python 3.9+ |
| Database | SQLite3 (dev), PostgreSQL (prod) |
| Task Queue | Celery + Redis |
| Server | Gunicorn (production) |
| Container | Docker & Docker Compose |

---

## 🚀 Moving to Production

### 1. Update Environment Variables
```bash
cp .env.example .env
# Edit .env with production values
```

### 2. Django Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### 3. PostgreSQL Database
```bash
# Uncomment PostgreSQL in settings.py
python manage.py migrate
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Collect Static Files
```bash
python manage.py collectstatic
```

### 6. Run with Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## ❓ Common Issues

### Port 8000 Already in Use
```bash
python manage.py runserver 8001
```

### Database Locked
```bash
rm db.sqlite3
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Permission Denied on Linux
```bash
chmod +x manage.py
```

---

## 📝 Next Steps

1. ✅ **Setup**: Complete - system is ready to use
2. 📅 **Add Courses**: Use admin panel to add courses
3. 👥 **Add Faculty**: Create faculty user accounts
4. 🏫 **Add Rooms**: Register available classrooms
5. ⏰ **Set Time Slots**: Configure available class times
6. 📊 **Generate Schedules**: Use constraint-based algorithm

---

## 📞 Support

- **Documentation**: See `README.md`
- **Issues**: Check `.env` and database connection
- **Admin Panel**: http://localhost:8000/admin

---

**© 2026 Carlos Hilado Memorial State University**
BS Information Systems • Faculty Scheduling System • AY 2025-2026
