# Blog System Project Documentation

## Project Overview

This is a blog system developed using the Django framework, featuring complete user management, article publishing, commenting, and other functionalities. The project employs modern web development technologies, including responsive design, RESTful APIs, and more.

## Technology Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Frontend**: HTML, CSS, JavaScript, Bootstrap

## Directory Structure

```
myblog/
├── .env                    # Environment variables configuration file
├── .git/                   # Git version control directory
├── .venv/                  # Python virtual environment
├── blog/                   # Blog core application
│   ├── admin.py            # Admin configuration
│   ├── models.py           # Data model definitions
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing configuration
│   ├── forms.py            # Form definitions
│   ├── serializers.py      # API serializers
│   ├── static/             # Blog app static files
│   └── templates/          # Blog app templates
├── blog_project/           # Project configuration directory
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── manage.py               # Django command-line tool
├── media/                  # User uploaded files
│   ├── avatars/            # User avatars
│   ├── post_covers/        # Article cover images
│   ├── profile_pics/       # Profile pictures
│   └── uploads/            # Other uploaded files
├── requirements.txt        # Project dependencies
├── run.sh                  # Startup script
├── static/                 # Collected static files
├── staticfiles/            # Static files source directory
├── templates/              # Global templates
└── users/                  # User management application
    ├── admin.py            # User admin management
    ├── models.py           # User data models
    ├── views.py            # User views
    ├── urls.py             # User URL configuration
    └── templates/          # User app templates
```

## Core Features

### Blog Application (blog)

- Creating, editing, publishing, and deleting articles
- Article category and tag management
- Comment system
- Article search
- Article archives

### User Application (users)

- User registration and login
- User profile management
- Avatar upload
- Permission control

## Database Configuration

The project uses PostgreSQL database. Database configuration is defined in the `.env` file:

```
DB_NAME=myblogdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## How to Run the Project

### Using Script

```bash
# Give the script execution permission
chmod +x run.sh

# Run the script
./run.sh
```

### Manual Run

```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Administrator Creation

```bash
python manage.py createsuperuser
```

## API Endpoints

The project provides RESTful APIs accessible via the following URLs:

- Article list: `/api/posts/`
- Article details: `/api/posts/<id>/`
- User information: `/api/users/`

## Deployment Instructions

### Production Environment Settings

1. Set `DEBUG=False` in the `.env` file
2. Set `ALLOWED_HOSTS` to your domain name
3. Configure static file service
4. Use Gunicorn or uWSGI as WSGI server
5. Use Nginx as reverse proxy

### Static File Collection

```bash
python manage.py collectstatic
```

## Common Issues and Solutions

1. **Database Connection Issues**
   - Check if PostgreSQL service is running
   - Verify database credentials in the `.env` file

2. **Static File Loading Issues**
   - Run `python manage.py collectstatic`
   - Check static file configuration in `settings.py`

3. **User Permission Issues**
   - Check user groups and permission settings
   - Ensure the user is logged in

## Maintenance and Updates

### Database Backup

```bash
pg_dump -U postgres myblogdb > backup.sql
```

### Application Updates

```bash
# Get the latest code
git pull

# Install new dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate
```

## Generate Article Slugs

```bash
python generate_slugs.py
```

## Development Guide

### Adding New Applications

```bash
python manage.py startapp new_app
```

Then add the new application to `INSTALLED_APPS` in `settings.py`.

### Creating Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing

```bash
python manage.py test
```

## Contribution Guidelines

1. Fork the project repository
2. Create a feature branch
3. Submit changes
4. Create a Pull Request

## License

[MIT License](LICENSE) 