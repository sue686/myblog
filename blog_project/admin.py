from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.db.models import Sum
from blog.models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

# 修改默认admin首页
@staff_member_required
def admin_dashboard(request, extra_context=None):
    """自定义管理员仪表盘，添加统计数据"""
    # 安全地获取统计数据
    try:
        post_count = Post.objects.count()
        user_count = User.objects.count()
        comment_count = Comment.objects.count()
        total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
        
        context = {
            'post_count': post_count,
            'user_count': user_count,
            'comment_count': comment_count,
            'total_views': total_views,
        }
    except Exception:
        # 如果出错，提供默认值
        context = {
            'post_count': 0,
            'user_count': 0,
            'comment_count': 0,
            'total_views': 0,
        }
    
    # 合并额外上下文（如果有）
    if extra_context:
        context.update(extra_context)
    
    return TemplateResponse(request, "admin/index.html", context)

# 不要直接替换默认的admin首页视图，使用urls.py中的配置代替
# admin.site.index = admin_dashboard 