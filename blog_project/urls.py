from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# 导入自定义AdminSite
from blog.admin import my_admin_site

urlpatterns = [
    path('admin/', my_admin_site.urls),  # 自定义 admin（主要使用）
    path('', RedirectView.as_view(url='/blog/', permanent=False)),
    path('blog/', include('blog.urls')),
    path('users/', include('users.urls')),
]

# 在开发环境中提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 