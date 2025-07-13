#!/bin/bash

echo "🔍 检查SSL证书路径和修复CSRF问题..."

# 检查可能的SSL证书路径
echo "📁 检查可能的SSL证书路径..."

# 常见的证书路径
CERT_PATHS=(
    "/etc/letsencrypt/live/selwyn-blog.duckdns.org"
    "/etc/ssl/certs/selwyn-blog.duckdns.org"
    "/home/ec2-user/ssl"
    "/opt/ssl"
    "/var/ssl"
)

CERT_FOUND=false
CERT_PATH=""

for path in "${CERT_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ 找到证书目录: $path"
        ls -la "$path"
        CERT_FOUND=true
        CERT_PATH="$path"
        break
    else
        echo "❌ 证书目录不存在: $path"
    fi
done

# 如果没找到证书，检查是否有其他证书
if [ "$CERT_FOUND" = false ]; then
    echo "🔍 搜索系统中的SSL证书..."
    find /etc -name "*.pem" -o -name "*.crt" 2>/dev/null | grep -i selwyn
    find /home -name "*.pem" -o -name "*.crt" 2>/dev/null | grep -i selwyn
    
    # 检查是否有任何Let's Encrypt证书
    if [ -d "/etc/letsencrypt/live" ]; then
        echo "📂 Let's Encrypt证书目录："
        ls -la /etc/letsencrypt/live/
    fi
fi

echo ""
echo "🔧 修复CSRF和安全设置..."

# 暂时禁用HTTPS要求，只使用HTTP
cat > nginx/nginx_temp.conf << 'EOF'
upstream web {
    server web:8000;
}

server {
    listen 80;
    server_name selwyn-blog.duckdns.org 3.26.32.171 localhost;
    
    # 增加超时时间
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # 静态文件处理
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 主应用代理
    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加缓冲区大小
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查端点
    location /health/ {
        proxy_pass http://web;
        access_log off;
    }
    
    # 指标端点
    location /metrics/ {
        proxy_pass http://web;
        access_log off;
    }
}
EOF

# 备份当前nginx配置
cp nginx/nginx.conf nginx/nginx.conf.backup

# 使用临时配置
cp nginx/nginx_temp.conf nginx/nginx.conf

echo "✅ 已更新nginx配置为HTTP-only模式"

# 创建Django settings补丁
cat > django_security_patch.py << 'EOF'
# Django安全设置补丁
import os

# 临时禁用HTTPS相关的安全设置
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 允许的主机
ALLOWED_HOSTS = [
    'selwyn-blog.duckdns.org',
    '3.26.32.171', 
    'localhost',
    '127.0.0.1'
]

# CSRF设置
CSRF_TRUSTED_ORIGINS = [
    'http://selwyn-blog.duckdns.org',
    'https://selwyn-blog.duckdns.org',
    'http://3.26.32.171',
    'https://3.26.32.171'
]

# 会话设置
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# 调试模式（临时）
DEBUG = True
EOF

echo "✅ 已创建Django安全设置补丁"

# 重启服务
echo "🔄 重启服务..."
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d

echo "⏳ 等待服务启动..."
sleep 30

# 测试访问
echo "🌐 测试网站访问..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://selwyn-blog.duckdns.org/)
echo "HTTP访问状态码: $HTTP_RESPONSE"

# 测试登录页面
LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://selwyn-blog.duckdns.org/users/login/)
echo "登录页面状态码: $LOGIN_RESPONSE"

if [ "$LOGIN_RESPONSE" = "200" ]; then
    echo "✅ 登录页面可以访问"
else
    echo "❌ 登录页面仍有问题"
    # 显示web容器日志
    echo "📝 Web容器日志："
    sudo docker-compose -f docker-compose.prod.yml logs --tail=10 web
fi

echo ""
echo "🎉 临时修复完成！"
echo ""
echo "📍 请通过HTTP访问网站："
echo "   - 主网站: http://selwyn-blog.duckdns.org"
echo "   - 登录页面: http://selwyn-blog.duckdns.org/users/login/"
echo "   - 管理后台: http://selwyn-blog.duckdns.org/admin/"
echo ""
echo "⚠️  注意：当前使用HTTP访问，SSL证书问题需要单独解决"
EOF

chmod +x check_ssl_and_fix.sh 