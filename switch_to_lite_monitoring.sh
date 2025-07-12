#!/bin/bash

echo "🚀 切换到轻量级监控配置..."

# 停止当前的监控服务
echo "📋 停止当前监控服务..."
cd /home/ec2-user/myblog
sudo docker-compose -f monitoring/docker-compose.monitoring.yml down

# 清理未使用的容器和镜像释放空间
echo "🧹 清理Docker资源..."
sudo docker system prune -f
sudo docker image prune -f

# 启动轻量级监控服务
echo "🔄 启动轻量级监控服务..."
sudo docker-compose -f monitoring/docker-compose.monitoring-lite.yml up -d

# 检查服务状态
echo "📊 检查服务状态..."
sudo docker ps

# 检查Django应用状态
echo "🌐 检查Django应用状态..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || echo "Django应用状态检查完成"

echo "✅ 轻量级监控配置部署完成！"
echo ""
echo "📍 可用服务："
echo "   - Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "   - Prometheus: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9090"
echo "   - Uptime Kuma: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3001"
echo "   - Node Exporter: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9100"
echo ""
echo "🎯 资源使用优化："
echo "   - 移除了 cAdvisor, AlertManager, Loki, Promtail (节省约400MB内存)"
echo "   - 添加了资源限制 (总共约550MB内存限制)"
echo "   - 减少了数据保留时间 (7天而不是15天)" 