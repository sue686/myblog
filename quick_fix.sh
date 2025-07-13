#!/bin/bash

echo "🚑 紧急修复：停止监控系统，恢复网站性能"

# 停止监控系统
echo "📋 停止监控系统..."
sudo docker-compose -f monitoring/docker-compose.monitoring.yml down || true

# 清理Docker资源
echo "🧹 清理Docker资源..."
sudo docker system prune -f

# 重启主应用
echo "🔄 重启主应用..."
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
sudo docker ps
echo ""
echo "📊 内存使用情况："
free -h
echo ""
echo "💾 磁盘使用情况："
df -h
echo ""

# 测试网站访问
echo "🌐 测试网站访问..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200"; then
    echo "✅ 网站恢复正常！"
    echo "🌐 访问地址: http://3.26.32.171"
else
    echo "❌ 网站仍有问题，请检查日志"
    sudo docker-compose -f docker-compose.prod.yml logs --tail=20
fi 