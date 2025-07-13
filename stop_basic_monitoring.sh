#!/bin/bash

# 停止基础监控系统脚本
echo "🛑 停止轻量级监控系统..."

# 停止监控服务
sudo docker-compose -f docker-compose.monitoring-basic.yml down

# 显示内存释放情况
echo "🖥️ 内存使用情况："
free -h

echo "✅ 监控系统已停止" 