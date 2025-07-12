#!/bin/bash

# 更新监控系统配置脚本
set -e

echo "🔄 更新监控系统配置..."

# 1. 备份原配置
echo "💾 备份原配置文件..."
cp monitoring/prometheus.yml monitoring/prometheus.yml.backup

# 2. 更新Prometheus配置
echo "⚙️ 更新Prometheus配置..."
cp monitoring/prometheus-updated.yml monitoring/prometheus.yml

# 3. 重启监控服务
echo "🔄 重启监控服务..."
cd monitoring
sudo docker-compose -f docker-compose.monitoring-lite.yml down
sudo docker-compose -f docker-compose.monitoring-lite.yml up -d

# 4. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 5. 验证服务状态
echo "🔍 验证服务状态..."
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo "Uptime Kuma: http://localhost:3001"

# 6. 测试指标收集
echo "📊 测试指标收集..."
curl -s http://localhost:9090/api/v1/query?query=up | grep -o '"result":\[.*\]' | head -1

echo "✅ 监控系统配置更新完成！"
echo "🌐 请访问 Grafana: http://selwyn-blog.duckdns.org:3000"
echo "🔒 用户名: admin, 密码: admin123" 