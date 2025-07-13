#!/bin/bash

# 启动轻量级监控系统
echo "🚀 启动轻量级监控系统..."

# 停止现有的监控服务
echo "🛑 停止现有监控服务..."
sudo docker-compose -f monitoring/docker-compose.monitoring.yml down 2>/dev/null || true
sudo docker-compose -f monitoring/docker-compose.monitoring-lite.yml down 2>/dev/null || true

# 清理可能存在的单独容器
echo "🧹 清理现有监控容器..."
sudo docker stop prometheus grafana node-exporter uptime-kuma 2>/dev/null || true
sudo docker rm prometheus grafana node-exporter uptime-kuma 2>/dev/null || true

# 启动轻量监控系统
echo "🚀 启动轻量监控服务..."
cd monitoring
sudo docker-compose -f docker-compose.monitoring-lite.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查监控服务状态..."
sudo docker-compose -f docker-compose.monitoring-lite.yml ps

echo "📊 检查内存使用情况..."
free -h

echo "✅ 轻量监控系统启动完成!"
echo ""
echo "🌐 监控访问地址："
echo "  - Grafana: http://3.26.32.171:3000 (admin/admin123)"
echo "  - Prometheus: http://3.26.32.171:9090"
echo "  - Node Exporter: http://3.26.32.171:9100"
echo "  - Uptime Kuma: http://3.26.32.171:3001"
echo ""
echo "🔒 如果无法访问，请检查安全组是否开放相应端口" 