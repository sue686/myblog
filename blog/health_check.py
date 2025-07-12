from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.conf import settings
import logging
import time
import psutil
import os
from datetime import datetime

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查端点
    """
    start_time = time.time()
    
    # 基础检查
    checks = {
        'database': check_database(),
        'disk_space': check_disk_space(),
        'memory': check_memory(),
        'dependencies': check_dependencies(),
    }
    
    # 计算响应时间
    response_time = round((time.time() - start_time) * 1000, 2)
    
    # 判断整体状态
    status = 'healthy' if all(check['status'] == 'ok' for check in checks.values()) else 'unhealthy'
    
    response_data = {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'response_time_ms': response_time,
        'checks': checks,
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'debug': settings.DEBUG,
    }
    
    # 记录日志
    if status == 'unhealthy':
        logger.error(f"Health check failed: {checks}")
    else:
        logger.info(f"Health check passed in {response_time}ms")
    
    return JsonResponse(response_data, status=200 if status == 'healthy' else 503)

def check_database():
    """检查数据库连接"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {
            'status': 'ok',
            'message': 'Database connection successful',
            'response_time_ms': 0  # 可以添加实际测量
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database connection failed: {str(e)}',
            'response_time_ms': 0
        }

def check_disk_space():
    """检查磁盘空间"""
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 10:
            status = 'warning'
            message = f'Low disk space: {free_percent:.1f}% free'
        elif free_percent < 5:
            status = 'error'
            message = f'Critical disk space: {free_percent:.1f}% free'
        else:
            status = 'ok'
            message = f'Disk space healthy: {free_percent:.1f}% free'
            
        return {
            'status': status,
            'message': message,
            'free_percent': round(free_percent, 1),
            'free_gb': round(disk_usage.free / (1024**3), 1),
            'total_gb': round(disk_usage.total / (1024**3), 1)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Disk space check failed: {str(e)}'
        }

def check_memory():
    """检查内存使用"""
    try:
        memory = psutil.virtual_memory()
        used_percent = memory.percent
        
        if used_percent > 90:
            status = 'error'
            message = f'Critical memory usage: {used_percent:.1f}%'
        elif used_percent > 80:
            status = 'warning'
            message = f'High memory usage: {used_percent:.1f}%'
        else:
            status = 'ok'
            message = f'Memory usage normal: {used_percent:.1f}%'
            
        return {
            'status': status,
            'message': message,
            'used_percent': round(used_percent, 1),
            'available_gb': round(memory.available / (1024**3), 1),
            'total_gb': round(memory.total / (1024**3), 1)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Memory check failed: {str(e)}'
        }

def check_dependencies():
    """检查依赖服务"""
    try:
        # 检查缓存（如果使用）
        # 检查队列（如果使用）
        # 检查外部API（如果使用）
        
        return {
            'status': 'ok',
            'message': 'All dependencies healthy',
            'services': {
                'redis': 'not_configured',
                'celery': 'not_configured',
                'external_apis': 'not_configured'
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Dependencies check failed: {str(e)}'
        }

@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    就绪检查端点 - 用于Kubernetes等容器编排
    """
    try:
        # 检查应用是否完全启动
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'ready',
            'message': 'Application is ready to serve requests',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'message': f'Application not ready: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=503)

@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    存活检查端点 - 用于容器存活性检查
    """
    return JsonResponse({
        'status': 'alive',
        'message': 'Application is running',
        'timestamp': datetime.now().isoformat(),
        'uptime': get_uptime()
    })

def get_uptime():
    """获取应用运行时间"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return {
            'seconds': int(uptime_seconds),
            'formatted': format_uptime(uptime_seconds)
        }
    except:
        return {
            'seconds': 0,
            'formatted': 'Unknown'
        }

def format_uptime(seconds):
    """格式化运行时间"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m" 