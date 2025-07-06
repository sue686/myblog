#!/bin/bash

# 数据迁移脚本：从现有PostgreSQL迁移到Docker环境
# 使用方法: chmod +x migrate_data.sh && ./migrate_data.sh

set -e

echo "🔄 开始数据迁移..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
OLD_DB_HOST="localhost"
OLD_DB_PORT="5432"
OLD_DB_NAME="myblogdb"
OLD_DB_USER="postgres"

NEW_DB_HOST="localhost"
NEW_DB_PORT="5432"  # Docker容器映射的端口
NEW_DB_NAME="myblogdb"
NEW_DB_USER="postgres"

BACKUP_DIR="./backups"
BACKUP_FILE="migration_backup_$(date +%Y%m%d_%H%M%S).sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo -e "${YELLOW}📦 步骤1: 备份现有数据库...${NC}"
if command -v pg_dump &> /dev/null; then
    PGPASSWORD="song@338" pg_dump -h $OLD_DB_HOST -p $OLD_DB_PORT -U $OLD_DB_USER -d $OLD_DB_NAME > "$BACKUP_DIR/$BACKUP_FILE"
    echo -e "${GREEN}✅ 数据库备份完成: $BACKUP_DIR/$BACKUP_FILE${NC}"
else
    echo -e "${RED}❌ pg_dump 未找到，请安装PostgreSQL客户端${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 步骤2: 检查备份文件大小...${NC}"
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
echo -e "${GREEN}备份文件大小: $BACKUP_SIZE${NC}"

echo -e "${YELLOW}🐳 步骤3: 启动Docker数据库容器...${NC}"
# 只启动数据库服务
docker-compose -f docker-compose.prod.yml up -d db

echo -e "${YELLOW}⏳ 等待数据库启动...${NC}"
sleep 15

# 检查数据库是否就绪
echo -e "${YELLOW}🔍 检查数据库连接...${NC}"
for i in {1..30}; do
    if PGPASSWORD="song@338" psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✅ 数据库连接成功${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 数据库连接超时${NC}"
        exit 1
    fi
    echo "尝试连接数据库... ($i/30)"
    sleep 2
done

echo -e "${YELLOW}🗑️ 步骤4: 清空Docker数据库（如果有数据）...${NC}"
PGPASSWORD="song@338" psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
" || true

echo -e "${YELLOW}📤 步骤5: 恢复数据到Docker数据库...${NC}"
PGPASSWORD="song@338" psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME < "$BACKUP_DIR/$BACKUP_FILE"
echo -e "${GREEN}✅ 数据恢复完成${NC}"

echo -e "${YELLOW}🔍 步骤6: 验证数据迁移...${NC}"
# 检查主要表的记录数
echo "检查数据表记录数:"
TABLES=("auth_user" "blog_post" "blog_comment" "blog_category" "blog_tag")

for table in "${TABLES[@]}"; do
    COUNT=$(PGPASSWORD="song@338" psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "0")
    echo "  $table: $COUNT 条记录"
done

echo -e "${YELLOW}📁 步骤7: 复制媒体文件...${NC}"
# 如果有媒体文件目录，复制到Docker卷
if [ -d "./media" ]; then
    echo "复制媒体文件到Docker卷..."
    # 这里需要根据实际情况调整路径
    docker-compose -f docker-compose.prod.yml exec -T web mkdir -p /app/media
    docker cp ./media/. $(docker-compose -f docker-compose.prod.yml ps -q web):/app/media/
    echo -e "${GREEN}✅ 媒体文件复制完成${NC}"
fi

echo -e "\n${GREEN}🎉 数据迁移完成！${NC}"
echo -e "${GREEN}📝 迁移摘要:${NC}"
echo -e "  备份文件: $BACKUP_DIR/$BACKUP_FILE"
echo -e "  备份大小: $BACKUP_SIZE"
echo -e "  迁移时间: $(date)"

echo -e "\n${YELLOW}📋 下一步操作:${NC}"
echo -e "1. 启动完整应用: docker-compose -f docker-compose.prod.yml up -d"
echo -e "2. 查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo -e "3. 测试网站功能"

echo -e "\n${YELLOW}⚠️ 重要提醒:${NC}"
echo -e "- 备份文件已保存，请妥善保管"
echo -e "- 如有问题，可以使用备份文件恢复"
echo -e "- 迁移完成后，建议测试所有主要功能" 