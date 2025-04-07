# Blog System Quick Start Guide

## Prerequisites

1. Ensure Python 3.9+ and PostgreSQL 12+ are installed
2. Ensure necessary development tools (Git, etc.) are installed

## 5-Minute Quick Start

### 1. Clone the Project and Enter Directory

```bash
git clone [repository URL]
cd myblog
```

### 2. Set Up Virtual Environment and Install Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

Ensure PostgreSQL is running, then create a database:

```bash
psql -U postgres
CREATE DATABASE myblogdb;
\q
```

Modify the database connection information in the `.env` file.

### 4. Run the Script

Add execute permission and run the script:

```bash
chmod +x run.sh
./run.sh
```

This script will execute database migrations and start the development server.

### 5. Access the Website

Open your browser and visit http://127.0.0.1:8000/

## Common Operations

### Create Administrator User

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

### Access Admin Backend

Open your browser and visit http://127.0.0.1:8000/admin/

Log in with the administrator account you just created.

### Publish New Article

1. Log in to the admin backend
2. Click the "Add" button under "Articles"
3. Fill in article title, content, and other information
4. Click the "Save" button

You can also create articles via the "Write Article" link in the navigation bar of the frontend (login required).

### Manage Users

1. Log in to the admin backend
2. Click "Users" management
3. View, modify, or create users

## Common Issues

### Cannot Connect to Database

- Check if PostgreSQL service is running
- Verify database credentials in the `.env` file are correct
- Ensure database `myblogdb` has been created

### Static Files Not Loading

Run the following command to collect static files:

```bash
python manage.py collectstatic
```

### Forgot Administrator Password

Reset administrator password:

```bash
python manage.py changepassword admin_username
```

## Basic Features Overview

### Blog Features

- Publish, edit, delete articles
- Article categories and tags
- Article comments
- Article search
- Article archives

### User Features

- User registration and login
- Profile management
- Avatar upload
- Permission control

## Next Steps

- View the complete [README.md](README.md) for more information
- Check [Development_Guide.md](Development_Guide.md) for technical details
- Want to contribute code? Please read the contribution guidelines first

## Quick Links

- Blog homepage: http://127.0.0.1:8000/blog/
- Admin backend: http://127.0.0.1:8000/admin/
- User login: http://127.0.0.1:8000/users/login/
- User registration: http://127.0.0.1:8000/users/register/ 