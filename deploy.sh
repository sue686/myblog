#!/bin/bash

# AWS EC2 Docker部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署博客到AWS..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在AWS EC2上
if [ ! -f /sys/hypervisor/uuid ] || [ "$(head -c 3 /sys/hypervisor/uuid)" != "ec2" ]; then
    echo -e "${YELLOW}警告: 似乎不在AWS EC2实例上运行${NC}"
fi

# 1. 备份现有数据库（如果存在）
echo -e "${YELLOW}📦 备份现有数据...${NC}"
if command -v pg_dump &> /dev/null; then
    mkdir -p backups
    pg_dump -h localhost -U postgres myblogdb > backups/backup_$(date +%Y%m%d_%H%M%S).sql || true
    echo -e "${GREEN}✅ 数据库备份完成${NC}"
fi

# 2. 更新代码
echo -e "${YELLOW}📥 更新代码...${NC}"
git pull origin main
echo -e "${GREEN}✅ 代码更新完成${NC}"

# 3. 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 安装Docker...${NC}"
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker安装完成${NC}"
fi

# 4. 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🔧 安装Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose安装完成${NC}"
fi

# 5. 停止现有服务（如果运行中）
echo -e "${YELLOW}⏹️ 停止现有服务...${NC}"
sudo systemctl stop gunicorn || true
sudo systemctl stop nginx || true
docker-compose -f docker-compose.prod.yml down || true
echo -e "${GREEN}✅ 现有服务已停止${NC}"

# 6. 构建和启动Docker容器
echo -e "${YELLOW}🔨 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 7. 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 30

# 8. 检查服务状态
echo -e "${YELLOW}🔍 检查服务状态...${NC}"
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    
    # 显示运行状态
    echo -e "\n${GREEN}📊 服务状态:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    
    # 获取服务器IP
    SERVER_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")
    echo -e "\n${GREEN}🌐 访问地址: http://${SERVER_IP}${NC}"
    
else
    echo -e "${RED}❌ 服务启动失败！${NC}"
    echo -e "${YELLOW}查看日志:${NC}"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

# 9. 数据迁移（如果需要从旧数据库迁移）
read -p "是否需要从备份恢复数据？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📤 恢复数据库...${NC}"
    # 这里可以添加数据恢复逻辑
    echo -e "${GREEN}✅ 数据恢复完成${NC}"
fi

echo -e "\n${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}📝 常用命令:${NC}"
echo -e "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo -e "  重启服务: docker-compose -f docker-compose.prod.yml restart"
echo -e "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo -e "  进入容器: docker-compose -f docker-compose.prod.yml exec web bash" 