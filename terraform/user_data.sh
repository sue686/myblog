#!/bin/bash

# EC2 User Data Script for ${project_name} - ${environment}
# This script runs on instance first boot

set -e

# Log all output
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting user data script for ${project_name} - ${environment}"

# Update system
echo "Updating system packages..."
yum update -y

# Install required packages
echo "Installing required packages..."
yum install -y \
    git \
    docker \
    curl \
    wget \
    htop \
    vim \
    unzip \
    aws-cli \
    postgresql-client \
    python3 \
    python3-pip \
    fail2ban \
    certbot

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configure Docker
echo "Configuring Docker..."
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install CloudWatch Agent
echo "Installing CloudWatch Agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Create CloudWatch Agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOL'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "metrics": {
    "namespace": "MyBlog/Application",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          "cpu_usage_idle",
          "cpu_usage_iowait",
          "cpu_usage_user",
          "cpu_usage_system"
        ],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [
          "used_percent"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "diskio": {
        "measurement": [
          "io_time"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 60
      },
      "netstat": {
        "measurement": [
          "tcp_established",
          "tcp_time_wait"
        ],
        "metrics_collection_interval": 60
      },
      "swap": {
        "measurement": [
          "swap_used_percent"
        ],
        "metrics_collection_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/user-data.log",
            "log_group_name": "/aws/ec2/${project_name}",
            "log_stream_name": "{instance_id}/user-data"
          },
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/aws/ec2/${project_name}",
            "log_stream_name": "{instance_id}/messages"
          },
          {
            "file_path": "/var/log/secure",
            "log_group_name": "/aws/ec2/${project_name}",
            "log_stream_name": "{instance_id}/secure"
          }
        ]
      }
    }
  }
}
EOL

# Start CloudWatch Agent
echo "Starting CloudWatch Agent..."
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

# Configure fail2ban
echo "Configuring fail2ban..."
systemctl start fail2ban
systemctl enable fail2ban

# Create fail2ban configuration for SSH
cat > /etc/fail2ban/jail.local << 'EOL'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/secure
EOL

systemctl restart fail2ban

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/myblog
chown ec2-user:ec2-user /opt/myblog

# Create backup directory
echo "Creating backup directory..."
mkdir -p /opt/backups
chown ec2-user:ec2-user /opt/backups

# Create monitoring scripts
echo "Creating monitoring scripts..."

# Health check script
cat > /opt/myblog/health_check.sh << 'EOL'
#!/bin/bash

# Health check script for MyBlog application
LOG_FILE="/var/log/health_check.log"

check_service() {
    local service_name=$1
    local check_command=$2
    
    echo "$(date): Checking $service_name..." >> $LOG_FILE
    
    if eval $check_command; then
        echo "$(date): $service_name is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): $service_name is unhealthy" >> $LOG_FILE
        return 1
    fi
}

# Check Docker containers
check_docker() {
    cd /opt/myblog
    docker-compose -f docker-compose.prod.yml ps | grep -q "Up"
}

# Check application endpoint
check_app() {
    curl -f http://localhost:8000/health/ > /dev/null 2>&1
}

# Check database
check_db() {
    cd /opt/myblog
    docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres
}

# Main health check
main() {
    echo "$(date): Starting health check..." >> $LOG_FILE
    
    failed=0
    
    if ! check_service "Docker containers" "check_docker"; then
        failed=1
    fi
    
    if ! check_service "Application" "check_app"; then
        failed=1
    fi
    
    if ! check_service "Database" "check_db"; then
        failed=1
    fi
    
    if [ $failed -eq 0 ]; then
        echo "$(date): All services are healthy" >> $LOG_FILE
        # Send success metric to CloudWatch
        aws cloudwatch put-metric-data --namespace "MyBlog/HealthCheck" --metric-data MetricName=HealthCheck,Value=1,Unit=Count --region ${AWS_DEFAULT_REGION:-ap-southeast-2}
    else
        echo "$(date): Some services are unhealthy" >> $LOG_FILE
        # Send failure metric to CloudWatch
        aws cloudwatch put-metric-data --namespace "MyBlog/HealthCheck" --metric-data MetricName=HealthCheck,Value=0,Unit=Count --region ${AWS_DEFAULT_REGION:-ap-southeast-2}
        
        # Attempt to restart services
        echo "$(date): Attempting to restart services..." >> $LOG_FILE
        cd /opt/myblog
        docker-compose -f docker-compose.prod.yml restart
        
        # Wait and check again
        sleep 30
        if check_service "Application after restart" "check_app"; then
            echo "$(date): Services restored successfully" >> $LOG_FILE
        else
            echo "$(date): Failed to restore services" >> $LOG_FILE
        fi
    fi
    
    echo "$(date): Health check completed" >> $LOG_FILE
}

main
EOL

chmod +x /opt/myblog/health_check.sh

# Backup script
cat > /opt/myblog/backup.sh << 'EOL'
#!/bin/bash

# Backup script for MyBlog application
BACKUP_DIR="/opt/backups"
S3_BUCKET="${backup_bucket:-myblog-backups}"
LOG_FILE="/var/log/backup.log"

echo "$(date): Starting backup process..." >> $LOG_FILE

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Database backup
echo "$(date): Creating database backup..." >> $LOG_FILE
cd /opt/myblog
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres myblogdb > $BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql

# Application files backup
echo "$(date): Creating application files backup..." >> $LOG_FILE
tar -czf $BACKUP_DIR/app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/myblog --exclude='*.log' --exclude='node_modules' --exclude='.git'

# Upload to S3
echo "$(date): Uploading backups to S3..." >> $LOG_FILE
aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/backups/$(date +%Y/%m/%d)/ --region ${AWS_DEFAULT_REGION:-ap-southeast-2}

# Clean up old local backups (keep last 7 days)
echo "$(date): Cleaning up old local backups..." >> $LOG_FILE
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "$(date): Backup process completed" >> $LOG_FILE
EOL

chmod +x /opt/myblog/backup.sh

# Create cron jobs
echo "Setting up cron jobs..."
cat > /tmp/crontab << 'EOL'
# Health check every 5 minutes
*/5 * * * * /opt/myblog/health_check.sh

# Backup every day at 2 AM
0 2 * * * /opt/myblog/backup.sh

# Clean up logs every week
0 0 * * 0 find /var/log -name "*.log" -mtime +7 -delete
EOL

crontab -u ec2-user /tmp/crontab

# Create logrotate configuration
cat > /etc/logrotate.d/myblog << 'EOL'
/var/log/health_check.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ec2-user ec2-user
}

/var/log/backup.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ec2-user ec2-user
}
EOL

# Configure firewall
echo "Configuring firewall..."
systemctl start firewalld
systemctl enable firewalld

# Allow SSH, HTTP, and HTTPS
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload

# Create environment file for applications
cat > /opt/myblog/.env << 'EOL'
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-southeast-2}
PROJECT_NAME=${project_name}
ENVIRONMENT=${environment}
EOL

chown ec2-user:ec2-user /opt/myblog/.env

# Create initial message
cat > /etc/motd << 'EOL'
Welcome to MyBlog Server!

This server is managed by Terraform and configured for:
- Project: ${project_name}
- Environment: ${environment}
- Region: ${AWS_DEFAULT_REGION:-ap-southeast-2}

Useful commands:
- Check application: systemctl status myblog
- View logs: journalctl -u myblog -f
- Health check: /opt/myblog/health_check.sh
- Backup: /opt/myblog/backup.sh

Application directory: /opt/myblog
Backup directory: /opt/backups
EOL

# Signal completion
echo "User data script completed successfully at $(date)"

# Send completion signal to CloudWatch
aws cloudwatch put-metric-data --namespace "MyBlog/Deployment" --metric-data MetricName=UserDataComplete,Value=1,Unit=Count --region ${AWS_DEFAULT_REGION:-ap-southeast-2}

echo "User data script finished" 