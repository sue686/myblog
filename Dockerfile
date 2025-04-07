FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 运行gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "blog_project.wsgi:application"] 