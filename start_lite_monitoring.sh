#!/bin/bash

echo "🚀 启动轻量级监控系统..."

# 检查内存情况
echo "📊 检查当前内存使用情况..."
free -h

# 确保主应用正在运行
echo "🔍 检查主应用状态..."
if ! sudo docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "⚠️  主应用未运行，先启动主应用..."
    sudo docker-compose -f docker-compose.prod.yml up -d
    sleep 30
fi

# 启动轻量级监控
echo "🔄 启动轻量级监控服务..."
sudo docker-compose -f monitoring/docker-compose.monitoring-lite.yml up -d

# 等待服务启动
echo "⏳ 等待监控服务启动..."
sleep 30

# 检查服务状态
echo "📋 检查监控服务状态..."
sudo docker-compose -f monitoring/docker-compose.monitoring-lite.yml ps

echo ""
echo "📊 系统资源使用情况："
free -h
echo ""
echo "🐳 Docker容器状态："
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 检查服务可用性
echo "🔍 检查服务可用性..."
sleep 10

# 检查主网站
if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200"; then
    echo "✅ 主网站正常"
else
    echo "❌ 主网站异常"
fi

# 检查Grafana
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ Grafana正常"
else
    echo "❌ Grafana异常"
fi

# 检查Prometheus
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9090 | grep -q "200"; then
    echo "✅ Prometheus正常"
else
    echo "❌ Prometheus异常"
fi

echo ""
echo "🎉 轻量级监控系统启动完成！"
echo ""
echo "📍 访问地址："
echo "   - 主网站: http://3.26.32.171"
echo "   - Grafana: http://3.26.32.171:3000 (admin/admin123)"
echo "   - Prometheus: http://3.26.32.171:9090"
echo "   - Uptime监控: http://3.26.32.171:3001"
echo ""
echo "💡 注意：轻量级监控只使用约550MB内存，适合t2.micro实例" 