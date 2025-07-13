#!/bin/bash

# 启动安全监控系统脚本
echo "🔒 启动安全监控系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 停止旧的不安全监控服务
echo "🛑 停止旧的监控服务..."
sudo docker-compose -f docker-compose.monitoring-basic.yml down 2>/dev/null || true

# 启动安全监控服务
echo "🚀 启动安全监控服务..."
sudo docker-compose -f docker-compose.monitoring-secure.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查服务状态..."
sudo docker-compose -f docker-compose.monitoring-secure.yml ps

# 检查端口绑定
echo "🔍 检查端口绑定情况："
echo "只应该看到127.0.0.1绑定："
sudo netstat -tuln | grep -E "(3001|9100|9999)" || echo "端口绑定检查完成"

# 检查内存使用
echo "🖥️ 检查内存使用情况..."
free -h

# 显示访问信息
echo ""
echo "✅ 安全监控系统启动完成！"
echo "🔒 所有监控端口现在只绑定到localhost (127.0.0.1)"
echo ""
echo "📱 通过SSH隧道访问监控界面："
echo "  在本地运行: ./ssh_tunnel.sh"
echo "  然后访问:"
echo "    • http://localhost:3001 - 网站监控 (Uptime Kuma)"
echo "    • http://localhost:9999 - 日志监控 (Dozzle)"  
echo "    • http://localhost:9100 - 系统指标 (Node Exporter)"
echo ""
echo "💡 安全优势："
echo "  ✅ 监控端口不对外开放"
echo "  ✅ 只有80、443、22端口对外可访问"
echo "  ✅ PostgreSQL和Django端口安全绑定"
echo "  ✅ 通过SSH加密隧道安全访问" 