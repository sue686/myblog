#!/bin/bash

echo "🚑 修复SSL网站性能问题..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📊 检查当前系统状态...${NC}"
echo "内存使用情况："
free -h
echo ""
echo "磁盘使用情况："
df -h
echo ""

# 1. 停止监控系统释放资源
echo -e "${YELLOW}📋 停止监控系统释放资源...${NC}"
sudo docker-compose -f monitoring/docker-compose.monitoring.yml down 2>/dev/null || true
sudo docker-compose -f monitoring/docker-compose.monitoring-lite.yml down 2>/dev/null || true

# 2. 清理Docker资源
echo -e "${YELLOW}🧹 清理Docker资源...${NC}"
sudo docker system prune -f
sudo docker image prune -f

# 3. 停止主应用
echo -e "${YELLOW}⏹️ 停止主应用...${NC}"
sudo docker-compose -f docker-compose.prod.yml down

# 4. 检查SSL证书
echo -e "${YELLOW}🔐 检查SSL证书...${NC}"
if [ -f "/etc/letsencrypt/live/selwyn-blog.duckdns.org/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL证书存在${NC}"
    ls -la /etc/letsencrypt/live/selwyn-blog.duckdns.org/
else
    echo -e "${RED}❌ SSL证书不存在，请检查路径${NC}"
fi

# 5. 更新代码
echo -e "${YELLOW}📥 更新代码...${NC}"
git pull origin main

# 6. 重新构建并启动服务
echo -e "${YELLOW}🔨 重新构建并启动服务...${NC}"
sudo docker-compose -f docker-compose.prod.yml build --no-cache
sudo docker-compose -f docker-compose.prod.yml up -d

# 7. 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 45

# 8. 检查服务状态
echo -e "${YELLOW}🔍 检查服务状态...${NC}"
sudo docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${YELLOW}📊 系统资源使用情况：${NC}"
free -h
echo ""

# 9. 测试网站访问
echo -e "${YELLOW}🌐 测试网站访问...${NC}"

# 测试HTTP重定向
echo "测试HTTP重定向..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://selwyn-blog.duckdns.org/)
if [ "$HTTP_RESPONSE" = "301" ] || [ "$HTTP_RESPONSE" = "302" ]; then
    echo -e "${GREEN}✅ HTTP重定向正常 (状态码: $HTTP_RESPONSE)${NC}"
else
    echo -e "${RED}❌ HTTP重定向异常 (状态码: $HTTP_RESPONSE)${NC}"
fi

# 测试HTTPS访问
echo "测试HTTPS访问..."
HTTPS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://selwyn-blog.duckdns.org/)
if [ "$HTTPS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ HTTPS访问正常 (状态码: $HTTPS_RESPONSE)${NC}"
else
    echo -e "${RED}❌ HTTPS访问异常 (状态码: $HTTPS_RESPONSE)${NC}"
fi

# 测试博客页面
echo "测试博客页面..."
BLOG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://selwyn-blog.duckdns.org/blog/)
if [ "$BLOG_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ 博客页面正常 (状态码: $BLOG_RESPONSE)${NC}"
else
    echo -e "${RED}❌ 博客页面异常 (状态码: $BLOG_RESPONSE)${NC}"
fi

# 10. 显示日志（如果有问题）
if [ "$HTTPS_RESPONSE" != "200" ] || [ "$BLOG_RESPONSE" != "200" ]; then
    echo -e "${YELLOW}📝 显示最近的日志...${NC}"
    echo "Web应用日志："
    sudo docker-compose -f docker-compose.prod.yml logs --tail=20 web
    echo ""
    echo "Nginx日志："
    sudo docker-compose -f docker-compose.prod.yml logs --tail=20 nginx
fi

echo ""
echo -e "${GREEN}🎉 修复完成！${NC}"
echo ""
echo -e "${GREEN}📍 访问地址：${NC}"
echo "   - 主网站: https://selwyn-blog.duckdns.org"
echo "   - 博客页面: https://selwyn-blog.duckdns.org/blog/"
echo "   - 管理后台: https://selwyn-blog.duckdns.org/admin/"
echo ""
echo -e "${GREEN}📊 系统状态：${NC}"
echo "   - 容器数量: $(sudo docker ps | wc -l) 个"
echo "   - 内存使用: $(free -h | grep Mem | awk '{print $3}')"
echo "   - 磁盘使用: $(df -h / | tail -1 | awk '{print $5}')"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 如果网站仍有问题，请检查SSL证书是否有效"
echo "   - 可以运行 'sudo docker-compose -f docker-compose.prod.yml logs -f' 查看实时日志"
echo "   - 监控系统已停止以节省资源" 