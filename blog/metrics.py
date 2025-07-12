from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.models import User
from blog.models import Post
import psutil
import time
import os
from datetime import datetime

@csrf_exempt
@never_cache
def metrics_view(request):
    """
    Prometheus指标端点
    """
    metrics = []
    
    # 添加标准指标格式
    metrics.append("# HELP django_info Django应用信息")
    metrics.append("# TYPE django_info gauge")
    metrics.append('django_info{version="5.0",app="myblog"} 1')
    
    # 数据库连接指标
    metrics.append("# HELP django_db_connections 数据库连接数")
    metrics.append("# TYPE django_db_connections gauge")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            active_connections = cursor.fetchone()[0]
        metrics.append(f"django_db_connections {{state=\"active\"}} {active_connections}")
    except:
        metrics.append("django_db_connections {state=\"active\"} 0")
    
    # 用户统计
    metrics.append("# HELP django_users_total 用户总数")
    metrics.append("# TYPE django_users_total gauge")
    try:
        user_count = User.objects.count()
        metrics.append(f"django_users_total {user_count}")
    except:
        metrics.append("django_users_total 0")
    
    # 博客文章统计
    metrics.append("# HELP django_posts_total 博客文章总数")
    metrics.append("# TYPE django_posts_total gauge")
    try:
        post_count = Post.objects.count()
        published_count = Post.objects.filter(status='published').count()
        metrics.append(f"django_posts_total {{status=\"all\"}} {post_count}")
        metrics.append(f"django_posts_total {{status=\"published\"}} {published_count}")
    except:
        metrics.append("django_posts_total {status=\"all\"} 0")
        metrics.append("django_posts_total {status=\"published\"} 0")
    
    # 系统资源指标
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append("# HELP system_cpu_usage_percent CPU使用率")
        metrics.append("# TYPE system_cpu_usage_percent gauge")
        metrics.append(f"system_cpu_usage_percent {cpu_percent}")
        
        # 内存使用
        memory = psutil.virtual_memory()
        metrics.append("# HELP system_memory_usage_bytes 内存使用量")
        metrics.append("# TYPE system_memory_usage_bytes gauge")
        metrics.append(f"system_memory_usage_bytes {{type=\"used\"}} {memory.used}")
        metrics.append(f"system_memory_usage_bytes {{type=\"available\"}} {memory.available}")
        metrics.append(f"system_memory_usage_bytes {{type=\"total\"}} {memory.total}")
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        metrics.append("# HELP system_disk_usage_bytes 磁盘使用量")
        metrics.append("# TYPE system_disk_usage_bytes gauge")
        metrics.append(f"system_disk_usage_bytes {{type=\"used\"}} {disk.used}")
        metrics.append(f"system_disk_usage_bytes {{type=\"free\"}} {disk.free}")
        metrics.append(f"system_disk_usage_bytes {{type=\"total\"}} {disk.total}")
        
    except Exception as e:
        metrics.append(f"# Error collecting system metrics: {e}")
    
    # HTTP请求指标（简单版本）
    metrics.append("# HELP django_http_requests_total HTTP请求总数")
    metrics.append("# TYPE django_http_requests_total counter")
    metrics.append("django_http_requests_total{method=\"GET\",status=\"200\"} 1")
    
    # 应用启动时间
    metrics.append("# HELP django_start_time_seconds 应用启动时间")
    metrics.append("# TYPE django_start_time_seconds gauge")
    start_time = time.time()
    metrics.append(f"django_start_time_seconds {start_time}")
    
    return HttpResponse('\n'.join(metrics), content_type='text/plain; version=0.0.4; charset=utf-8') 