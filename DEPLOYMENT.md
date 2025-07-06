# 🚀 Deployment Guide - Django Blog System

This document provides comprehensive deployment instructions for the Django Blog System, covering both development and production environments.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Development](#docker-development)
4. [Production Deployment](#production-deployment)
5. [AWS EC2 Deployment](#aws-ec2-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Database Migration](#database-migration)
8. [SSL/HTTPS Setup](#ssl-https-setup)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / Amazon Linux 2023 / macOS / Windows 10+
- **Python**: 3.11 or higher
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: Minimum 10GB free space

### Development Tools
- Code editor (VS Code, PyCharm, etc.)
- Terminal/Command line access
- SSH client (for remote deployment)

## 🏠 Local Development

### 1. Clone Repository
```bash
git clone https://github.com/sue686/myblog.git
cd myblog
```

### 2. Python Virtual Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Create environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 6. Static Files Collection
```bash
python manage.py collectstatic --noinput
```

### 7. Start Development Server
```bash
# Using Django development server
python manage.py runserver

# Or using the provided script
chmod +x run.sh
./run.sh
```

### 8. Access Application
- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/

## 🐳 Docker Development

### 1. Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### 2. Initialize Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 3. Useful Docker Commands
```bash
# View logs
docker-compose logs -f web

# Execute commands in container
docker-compose exec web bash

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build web
```

## 🌐 Production Deployment

### Architecture Overview
```
Internet → AWS Load Balancer → EC2 Instance → Nginx → Django (Gunicorn) → PostgreSQL
```

### Production Environment Features
- **High Availability**: Multiple container instances
- **Load Balancing**: Nginx reverse proxy
- **Database**: PostgreSQL with persistent volumes
- **Static Files**: Nginx static file serving
- **Security**: SSL/TLS encryption
- **Monitoring**: Container health checks
- **Backup**: Automated database backups

## ☁️ AWS EC2 Deployment

### Step 1: AWS Infrastructure Setup

#### 1.1 Launch EC2 Instance
```bash
# Instance specifications:
# - Instance Type: t3.medium (2 vCPU, 4GB RAM) minimum
# - AMI: Ubuntu 20.04 LTS or Amazon Linux 2023
# - Storage: 20GB GP3 SSD minimum
# - Security Group: Allow ports 22, 80, 443, 8000
```

#### 1.2 Security Group Configuration
```bash
# Inbound Rules:
# SSH (22) - Your IP
# HTTP (80) - 0.0.0.0/0
# HTTPS (443) - 0.0.0.0/0
# Custom TCP (8000) - 0.0.0.0/0 (for testing)
```

#### 1.3 Key Pair Setup
```bash
# Create or use existing key pair
# Download .pem file and set permissions
chmod 400 your-key.pem
```

### Step 2: Server Preparation

#### 2.1 Connect to Instance
```bash
# For Ubuntu
ssh -i your-key.pem ubuntu@your-ec2-ip

# For Amazon Linux
ssh -i your-key.pem ec2-user@your-ec2-ip
```

#### 2.2 System Updates
```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# Amazon Linux
sudo yum update -y
```

#### 2.3 Install Required Packages
```bash
# Ubuntu
sudo apt install -y git docker.io docker-compose-plugin

# Amazon Linux
sudo yum install -y git docker
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2.4 Configure Docker
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again for group changes to take effect
exit
# Reconnect via SSH
```

### Step 3: Application Deployment

#### 3.1 Clone Repository
```bash
git clone https://github.com/sue686/myblog.git
cd myblog
```

#### 3.2 Automated Deployment

**Option A: Fresh Deployment (New Server)**
```bash
chmod +x deploy_fresh.sh
./deploy_fresh.sh
```

**Option B: Update Deployment (Existing Server)**
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 3.3 Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Configure environment
cp .env.example .env.prod
nano .env.prod

# 2. Build and start services
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 3. Wait for services to start
sleep 30

# 4. Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 5. Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 6. Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Step 4: Verify Deployment

#### 4.1 Check Service Status
```bash
# View running containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs web
```

#### 4.2 Test Application
```bash
# Get your EC2 public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Test website
curl http://YOUR-EC2-IP

# Test admin panel
curl http://YOUR-EC2-IP/admin/
```

## ⚙️ Environment Configuration

### Development Environment (.env)
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-dev-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=myblogdb
DB_USER=postgres
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production Environment (.env.prod)
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR-EC2-IP

# Database Configuration
DB_NAME=myblogdb
DB_USER=postgres
DB_PASSWORD=secure_production_password
DB_HOST=db
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 📊 Database Migration

### From SQLite to PostgreSQL

#### 1. Export Data from SQLite
```bash
# On local machine
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
```

#### 2. Transfer Data to Production
```bash
# Upload to server
scp -i your-key.pem data.json ubuntu@your-ec2-ip:~/myblog/
```

#### 3. Import Data to PostgreSQL
```bash
# On production server
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata data.json
```

### Backup and Restore

#### Database Backup
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres myblogdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres myblogdb > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

#### Database Restore
```bash
# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres myblogdb < backup_file.sql
```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt with Certbot

#### 1. Install Certbot
```bash
# Ubuntu
sudo apt install certbot python3-certbot-nginx

# Amazon Linux
sudo yum install certbot python3-certbot-nginx
```

#### 2. Obtain SSL Certificate
```bash
# Stop nginx container temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Certificates will be saved to /etc/letsencrypt/live/your-domain.com/
```

#### 3. Update Nginx Configuration
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }

        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 4. Update Docker Compose
```yaml
# docker-compose.prod.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    - static_volume:/app/staticfiles
    - media_volume:/app/media
    - /etc/letsencrypt:/etc/letsencrypt
  depends_on:
    - web
  restart: unless-stopped
```

#### 5. Auto-renewal Setup
```bash
# Add to crontab
sudo crontab -e

# Add this line for automatic renewal
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /path/to/your/project/docker-compose.prod.yml restart nginx
```

## 📈 Monitoring & Maintenance

### Health Checks

#### 1. Application Health Check
```bash
#!/bin/bash
# health_check.sh
HEALTH_URL="http://YOUR-EC2-IP/health/"
if curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "Application is healthy"
else
    echo "Application is down - restarting services"
    cd /path/to/your/project
    docker-compose -f docker-compose.prod.yml restart
fi
```

#### 2. Database Health Check
```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

### Log Management

#### 1. Application Logs
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Log rotation setup
sudo nano /etc/logrotate.d/docker-logs
```

#### 2. System Monitoring
```bash
# Monitor system resources
docker stats

# Monitor disk usage
df -h

# Monitor memory usage
free -h
```

### Automated Maintenance

#### 1. Maintenance Script
```bash
#!/bin/bash
# maintenance.sh
echo "Starting maintenance..."

# Update code
git pull origin main

# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres myblogdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Update containers
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Clean up old images
docker system prune -f

echo "Maintenance completed"
```

#### 2. Cron Jobs
```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh

# Weekly maintenance at 3 AM on Sunday
0 3 * * 0 /path/to/maintenance.sh
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs web

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Rebuild container
docker-compose -f docker-compose.prod.yml build --no-cache web
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Reset database connection
docker-compose -f docker-compose.prod.yml restart db
docker-compose -f docker-compose.prod.yml restart web
```

#### 3. Static Files Not Loading
```bash
# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 4. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/your/project

# Fix docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

#### 5. Memory Issues
```bash
# Check memory usage
free -h

# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Performance Optimization

#### 1. Database Optimization
```bash
# Optimize database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d myblogdb -c "VACUUM ANALYZE;"

# Check slow queries
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d myblogdb -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

#### 2. Container Resource Limits
```yaml
# docker-compose.prod.yml
web:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Review this documentation
3. Search existing GitHub issues
4. Create a new issue with detailed information

## 🔄 Continuous Deployment

For automated deployments, consider setting up:
- GitHub Actions for CI/CD
- AWS CodeDeploy for deployment automation
- Docker Hub for image registry
- Monitoring tools like Prometheus and Grafana

---

**Happy Deploying! 🚀** 