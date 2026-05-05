# Faculty Scheduling System - Constraint-Based Optimization

A professional web application for managing faculty scheduling at Carlos Hilado Memorial State University using constraint-based optimization algorithms.

## Project Overview

The Faculty Scheduling System helps university departments optimize faculty scheduling using constraint-based algorithms to ensure:
- Efficient resource allocation
- Conflict-free timetabling
- Balanced teaching workloads
- AI-powered faculty assignments

### Key Features
- **Automated Scheduling**: AI-powered faculty assignment and course scheduling
- **Load Management**: Balance teaching workloads across faculty
- **Multi-role Support**: Admin, Dean, Department Head, and Faculty roles
- **Schedule Management**: Create, publish, and manage class schedules
- **Reporting**: Generate insights and analytics

## Tech Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript (Vanilla)

### Backend
- Python 3.9+
- Django 4.2
- Django REST Framework
- PostgreSQL (development and production)

### Additional Technologies
- Celery (Task Queue)
- Redis (Caching & Message Broker)
- Gunicorn (WSGI Server)
- WhiteNoise (Static Files)

## Project Structure

```
AFS/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
│
├── config/                  # Main project configuration
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI application
│
├── apps/                    # Django applications
│   ├── core/               # Core app (homepage, dashboard)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── authentication/     # User authentication
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   └── scheduling/         # Scheduling functionality
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       └── apps.py
│
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── authentication/
│   │   └── login.html     # Login page
│   ├── core/
│   │   └── dashboard.html # Dashboard page
│   └── scheduling/
│       ├── schedule_list.html
│       └── schedule_detail.html
│
└── static/                 # Static files
    ├── css/
    │   └── style.css      # Custom CSS
    └── js/
        └── main.js        # Custom JavaScript
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- PostgreSQL 12+ (for production)
- Redis (optional, for caching)

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AFS
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/faculty_scheduling
   ```

5. **Create the PostgreSQL schema and seed data**
   ```bash
   python setup_database.py
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files** (development)
   ```bash
   python manage.py collectstatic
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

Open your browser and visit: `http://localhost:8000`

### Demo Credentials
- **Username**: admin
- **Password**: admin123

## Database Models

### Authentication App
- **User**: Extended Django User model with role and department fields

### Core App
- **SystemSettings**: System configuration

### Scheduling App
- **Department**: University departments
- **Course**: Courses offered by departments
- **Room**: Classrooms and teaching spaces
- **TimeSlot**: Available time slots
- **Schedule**: Class schedule assignments

## User Roles

1. **Administrator**: Full system access, user and system management
2. **Dean**: Department oversight, schedule approval
3. **Department Head**: Manage department schedules and faculty
4. **Faculty**: View personal schedules and assignments

## API Endpoints

### Authentication
- `POST /auth/login/` - User login
- `GET /auth/logout/` - User logout

### Core
- `GET /` - Landing page / Dashboard
- `GET /dashboard/` - User dashboard

### Scheduling
- `GET /scheduling/` - View all schedules
- `GET /scheduling/<id>/` - View schedule details

## Production Deployment

### Switch to PostgreSQL

1. **Install PostgreSQL adapter**
   ```bash
   pip install psycopg2-binary
   ```

2. **Set `DATABASE_URL` or the individual `DATABASE_*` variables**
   ```python
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/faculty_scheduling
   ```

3. **Create database**
   ```bash
   createdb faculty_scheduling
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

### Security Settings for Production

Update `config/settings.py`:
```python
DEBUG = False
SECRET_KEY = 'your-strong-secret-key'
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### Deployment with Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Testing

Run tests:
```bash
python manage.py test
```

With coverage:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Maintenance

### Create a superuser
```bash
python manage.py createsuperuser
```

### Access admin panel
Visit: `http://localhost:8000/admin/`

### Make migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Load sample data
```bash
python manage.py loaddata sample_data
```

## Common Issues

### Port already in use
```bash
python manage.py runserver 0.0.0.0:8001
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

### Database errors
```bash
python manage.py migrate --verbosity 2
```

## Contributing

1. Create a new branch for features
2. Follow PEP 8 style guide
3. Write tests for new features
4. Submit pull request with clear description

## License

This project is developed for Carlos Hilado Memorial State University.

## Support

For issues or questions, contact the development team or create an issue in the repository.

## Author

Developed by: Claude Code (AI Assistant)
Date: 2026-05-03

---

**© 2026 Carlos Hilado Memorial State University**
BS Information Systems • Faculty Scheduling System Using Constraint-Based Optimization • AY 2025-2026
