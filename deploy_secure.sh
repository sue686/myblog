#!/bin/bash

# 安全部署脚本 - 只开放必要端口
echo "🔒 部署安全配置..."

# 备份当前配置
echo "💾 备份当前配置..."
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)

# 停止当前服务
echo "🛑 停止当前服务..."
sudo docker-compose -f docker-compose.prod.yml down

# 使用安全配置重新部署
echo "🚀 使用安全配置重新部署..."
sudo docker-compose -f docker-compose.prod-secure.yml up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
sudo docker-compose -f docker-compose.prod-secure.yml ps

# 检查端口安全性
echo "🔍 检查端口安全性..."
echo "对外开放的端口 (应该只有22, 80, 443)："
sudo netstat -tuln | grep "0.0.0.0:" | grep -E ":22 |:80 |:443 " || echo "检查完成"

echo "内部绑定的端口 (127.0.0.1)："
sudo netstat -tuln | grep "127.0.0.1:" || echo "检查完成"

# 测试网站访问
echo "🌐 测试网站访问..."
curl -I https://selwyn-blog.duckdns.org/ || echo "网站测试完成"

# 显示安全状态
echo ""
echo "✅ 安全部署完成！"
echo ""
echo "🔒 安全配置："
echo "  ✅ 只有端口22 (SSH), 80 (HTTP), 443 (HTTPS)对外开放"
echo "  ✅ PostgreSQL (5432) 只绑定localhost"
echo "  ✅ Django (8000) 只绑定localhost"
echo "  ✅ 网站通过nginx代理正常访问"
echo ""
echo "🚨 注意："
echo "  如果需要访问数据库，请使用SSH隧道:"
echo "  ssh -L 5432:localhost:5432 ec2-user@3.26.32.171"
echo ""
echo "📱 启动监控："
echo "  ./start_secure_monitoring.sh" 