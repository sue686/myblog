#!/bin/bash

# AWS EC2 全新Docker部署脚本
# 使用方法: chmod +x deploy_fresh.sh && ./deploy_fresh.sh

set -e  # 遇到错误立即退出

echo "🚀 开始全新部署博客到AWS..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 更新代码
echo -e "${YELLOW}📥 更新代码...${NC}"
git pull origin main
echo -e "${GREEN}✅ 代码更新完成${NC}"

# 2. 停止所有现有服务
echo -e "${YELLOW}⏹️ 停止现有服务...${NC}"
sudo systemctl stop gunicorn || true
sudo systemctl stop nginx || true
sudo systemctl stop postgresql || true
docker-compose -f docker-compose.prod.yml down || true
docker system prune -f || true
echo -e "${GREEN}✅ 现有服务已停止${NC}"

# 3. 检查并安装Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 安装Docker...${NC}"
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker安装完成${NC}"
    echo -e "${BLUE}ℹ️ 注意：可能需要重新登录以使Docker组权限生效${NC}"
fi

# 4. 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🔧 安装Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose安装完成${NC}"
fi

# 5. 清理旧的Docker数据（如果有）
echo -e "${YELLOW}🗑️ 清理旧数据...${NC}"
docker volume rm myblog_postgres_data || true
docker volume rm myblog_static_volume || true
docker volume rm myblog_media_volume || true
echo -e "${GREEN}✅ 旧数据清理完成${NC}"

# 6. 构建和启动服务
echo -e "${YELLOW}🔨 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 7. 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 45

# 8. 创建超级用户
echo -e "${YELLOW}👤 创建超级用户...${NC}"
echo "请按提示创建管理员账户："
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 9. 检查服务状态
echo -e "${YELLOW}🔍 检查服务状态...${NC}"
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    
    # 显示运行状态
    echo -e "\n${GREEN}📊 服务状态:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    
    # 获取服务器IP
    SERVER_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")
    echo -e "\n${GREEN}🌐 访问地址:${NC}"
    echo -e "  主页: http://${SERVER_IP}"
    echo -e "  管理后台: http://${SERVER_IP}/admin/"
    
else
    echo -e "${RED}❌ 服务启动失败！${NC}"
    echo -e "${YELLOW}查看日志:${NC}"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

# 10. 添加示例数据（可选）
read -p "是否添加示例分类和标签？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📝 添加示例数据...${NC}"
    docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from blog.models import Category, Tag

# 创建分类
categories = ['Technology', 'Programming', 'Web Development', 'AI & ML', 'Career']
for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)

# 创建标签
tags = ['Python', 'Django', 'JavaScript', 'React', 'Docker', 'AWS', 'PostgreSQL', 'CSS', 'HTML', 'Git']
for tag_name in tags:
    Tag.objects.get_or_create(name=tag_name)

print('示例数据添加完成！')
"
    echo -e "${GREEN}✅ 示例数据添加完成${NC}"
fi

echo -e "\n${GREEN}🎉 全新部署完成！${NC}"
echo -e "${GREEN}📝 常用命令:${NC}"
echo -e "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo -e "  重启服务: docker-compose -f docker-compose.prod.yml restart"
echo -e "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo -e "  进入容器: docker-compose -f docker-compose.prod.yml exec web bash"
echo -e "  查看数据库: docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d myblogdb"

echo -e "\n${BLUE}📋 下一步:${NC}"
echo -e "1. 访问网站确认功能正常"
echo -e "2. 登录管理后台添加内容"
echo -e "3. 配置域名和SSL证书（如需要）"

echo -e "\n${YELLOW}⚠️ 提醒:${NC}"
echo -e "- 这是全新部署，没有历史数据"
echo -e "- 管理员账户已创建，请妥善保管密码"
echo -e "- 如需要域名，记得配置DNS解析" 