#!/bin/bash

# 更新静态文件配置脚本
echo "开始更新服务器代码和重新部署..."

# 拉取最新代码
echo "拉取最新代码..."
git pull origin main

# 停止现有容器
echo "停止现有容器..."
sudo docker-compose -f docker-compose.prod.yml down

# 重新构建并启动容器
echo "重新构建并启动容器..."
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 20

# 检查服务状态
echo "检查服务状态..."
sudo docker-compose -f docker-compose.prod.yml ps

# 测试静态文件访问
echo "测试静态文件访问..."
curl -I https://selwyn-blog.duckdns.org/static/blog/css/style.css

echo "更新完成！"
echo "请访问 https://selwyn-blog.duckdns.org 查看网站是否正常显示" 