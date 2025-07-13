#!/bin/bash

# 内存监控脚本
LOG_FILE="/var/log/memory_monitor.log"
MEMORY_THRESHOLD=70  # 内存使用率告警阈值
DISK_THRESHOLD=90    # 磁盘使用率告警阈值

# 获取内存使用率
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
MEMORY_USAGE_INT=${MEMORY_USAGE%.*}

# 获取磁盘使用率
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 记录日志
echo "[$TIMESTAMP] 内存使用率: ${MEMORY_USAGE}% | 磁盘使用率: ${DISK_USAGE}%" >> $LOG_FILE

# 检查内存使用率
if [ "$MEMORY_USAGE_INT" -gt "$MEMORY_THRESHOLD" ]; then
    echo "⚠️ 内存告警！当前使用率: ${MEMORY_USAGE}%"
    echo "📊 详细信息："
    free -h
    echo "🐳 Docker容器内存使用："
    docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
    
    # 记录告警日志
    echo "[$TIMESTAMP] 🚨 内存告警: ${MEMORY_USAGE}%" >> $LOG_FILE
fi

# 检查磁盘使用率
if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    echo "⚠️ 磁盘告警！当前使用率: ${DISK_USAGE}%"
    echo "📊 磁盘详细信息："
    df -h
    
    # 记录告警日志
    echo "[$TIMESTAMP] 🚨 磁盘告警: ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查Docker容器状态
echo "🐳 Docker容器状态："
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 如果内存使用率正常，显示简要信息
if [ "$MEMORY_USAGE_INT" -le "$MEMORY_THRESHOLD" ] && [ "$DISK_USAGE" -le "$DISK_THRESHOLD" ]; then
    echo "✅ 系统状态正常 - 内存: ${MEMORY_USAGE}% | 磁盘: ${DISK_USAGE}% | 时间: $TIMESTAMP"
fi 