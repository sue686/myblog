from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .admin import admin_dashboard

# 自定义管理界面标题
admin.site.site_header = "博客管理系统"
admin.site.site_title = "博客管理后台"  
admin.site.index_title = "欢迎使用博客管理系统"

urlpatterns = [
    path('', RedirectView.as_view(url='/blog/'), name='home_redirect'),
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),  # 添加自定义dashboard
    path('users/', include('users.urls')),
    path('blog/', include('blog.urls')),
    
    # 添加网站图标路由
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('blog/images/favicon.ico')), name='favicon'),
    path('apple-touch-icon.png', RedirectView.as_view(url=staticfiles_storage.url('blog/images/apple-touch-icon.png')), name='apple-touch-icon'),
    path('apple-touch-icon-precomposed.png', RedirectView.as_view(url=staticfiles_storage.url('blog/images/apple-touch-icon.png')), name='apple-touch-icon-precomposed'),
] 

# 添加媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 