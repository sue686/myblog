#!/bin/bash

# 启动基础监控系统脚本
echo "🔧 启动轻量级监控系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 启动基础监控服务
echo "🚀 启动监控服务..."
sudo docker-compose -f docker-compose.monitoring-basic.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查服务状态..."
sudo docker-compose -f docker-compose.monitoring-basic.yml ps

# 检查内存使用
echo "🖥️ 检查内存使用情况..."
free -h

# 显示访问地址
echo ""
echo "✅ 监控系统启动完成！"
echo "📱 访问地址："
echo "  • 网站监控: http://3.26.32.171:3001"
echo "  • 日志监控: http://3.26.32.171:9999"
echo "  • 系统指标: http://3.26.32.171:9100"
echo ""
echo "💡 建议设置："
echo "  1. 在Uptime Kuma中添加网站监控"
echo "  2. 设置内存使用超过70%时告警"
echo "  3. 设置磁盘空间超过90%时告警"
echo "  4. 设置网站响应时间超过5秒时告警" 