from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/blog/'), name='home_redirect'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('blog/', include('blog.urls')),
] 

# 添加媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 