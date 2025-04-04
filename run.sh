#!/bin/bash

# 设置环境变量
export DB_NAME=myblogdb
export DB_USER=postgres
export DB_PASSWORD=song@338
export DB_HOST=localhost
export DB_PORT=5432

# 激活虚拟环境（如果需要）
source .venv/bin/activate

# 运行迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver 