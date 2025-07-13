#!/bin/bash

# SSH隧道脚本 - 安全访问服务器监控界面
# 使用方法：./ssh_tunnel.sh

echo "🔒 创建SSH隧道访问监控界面..."

# 服务器配置
SERVER_HOST="3.26.32.171"
SERVER_USER="ec2-user"

# 检查SSH密钥
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "❌ 未找到SSH密钥文件 ~/.ssh/id_rsa"
    echo "💡 请确保你有服务器的SSH访问权限"
    echo "   或者使用: ssh-keygen -t rsa 生成密钥对"
    exit 1
fi

echo "🚀 正在建立SSH隧道..."
echo "📱 建立后可以访问："
echo "  • http://localhost:3001 - 网站监控 (Uptime Kuma)"
echo "  • http://localhost:9999 - 日志监控 (Dozzle)"
echo "  • http://localhost:9100 - 系统指标 (Node Exporter)"
echo ""
echo "⚠️ 保持此终端运行，按Ctrl+C断开隧道"
echo ""

# 创建SSH隧道
# -L: 本地端口转发
# -N: 不执行远程命令
# -f: 后台运行 (可选)
ssh -L 3001:localhost:3001 \
    -L 9999:localhost:9999 \
    -L 9100:localhost:9100 \
    -N -o StrictHostKeyChecking=no \
    ${SERVER_USER}@${SERVER_HOST}

echo "🔒 SSH隧道已断开" 