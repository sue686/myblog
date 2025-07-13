#!/bin/bash

# 本地SSH隧道脚本 - 用于安全访问服务器监控界面
# 运行此脚本后，可以在本地浏览器安全访问监控界面

echo "🔑 创建安全监控SSH隧道..."

# 检查SSH私钥是否存在
if [ ! -f ~/.ssh/myblog-key.pem ]; then
    echo "❌ 找不到SSH私钥: ~/.ssh/myblog-key.pem"
    echo "请确保SSH私钥文件在正确位置"
    exit 1
fi

# 检查私钥权限
chmod 600 ~/.ssh/myblog-key.pem

echo "🌐 正在建立SSH隧道连接到 3.26.32.171..."
echo "📊 隧道端口映射:"
echo "  - 本地 3001 -> 远程 Uptime Kuma (127.0.0.1:3001)"
echo "  - 本地 9100 -> 远程 Node Exporter (127.0.0.1:9100)"
echo "  - 本地 9999 -> 远程 Dozzle 日志 (127.0.0.1:9999)"
echo ""
echo "🔗 隧道建立后，可以在浏览器访问:"
echo "  - 网站监控: http://localhost:3001"
echo "  - 系统监控: http://localhost:9100"
echo "  - 日志监控: http://localhost:9999"
echo ""
echo "⚠️  保持此终端窗口开启以维持隧道连接"
echo "📱 按 Ctrl+C 退出隧道"
echo ""

# 建立SSH隧道
ssh -i ~/.ssh/myblog-key.pem \
    -L 3001:127.0.0.1:3001 \
    -L 9100:127.0.0.1:9100 \
    -L 9999:127.0.0.1:9999 \
    -N \
    ec2-user@3.26.32.171

echo "🔒 SSH隧道已关闭" 