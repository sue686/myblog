#!/bin/bash

# 部署安全监控系统
# 这个脚本会启动轻量级、安全的监控系统（只绑定localhost）

echo "🔒 部署安全监控系统..."

# 检查是否有安全监控配置文件
if [ ! -f "docker-compose.monitoring-secure.yml" ]; then
    echo "❌ 找不到安全监控配置文件: docker-compose.monitoring-secure.yml"
    exit 1
fi

# 停止现有的不安全监控（如果存在）
echo "🛑 停止现有的不安全监控..."
sudo docker-compose -f docker-compose.monitoring-lite.yml down 2>/dev/null || true
sudo docker-compose -f docker-compose.monitoring.yml down 2>/dev/null || true

# 确保先停止可能冲突的单独容器
echo "🧹 清理可能冲突的容器..."
sudo docker stop node-exporter uptime-kuma dozzle 2>/dev/null || true
sudo docker rm node-exporter uptime-kuma dozzle 2>/dev/null || true

# 启动安全监控系统
echo "🚀 启动安全监控系统..."
sudo docker-compose -f docker-compose.monitoring-secure.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
sudo docker-compose -f docker-compose.monitoring-secure.yml ps

# 显示内存使用情况
echo "📊 当前内存使用情况:"
free -h

# 显示监控端口（只绑定localhost）
echo "🔗 监控端口（只能通过SSH隧道访问）:"
echo "  - Node Exporter: 127.0.0.1:9100"
echo "  - Uptime Kuma: 127.0.0.1:3001"
echo "  - Dozzle (日志): 127.0.0.1:9999"

# 显示SSH隧道命令
echo ""
echo "🔑 SSH隧道命令 (在本地电脑运行):"
echo "ssh -i ~/.ssh/myblog-key.pem -L 3001:127.0.0.1:3001 -L 9100:127.0.0.1:9100 -L 9999:127.0.0.1:9999 ec2-user@3.26.32.171"
echo ""
echo "然后在本地浏览器访问:"
echo "  - http://localhost:3001 (Uptime Kuma)"
echo "  - http://localhost:9100 (Node Exporter)"
echo "  - http://localhost:9999 (Dozzle)"

echo "✅ 安全监控部署完成!" 