from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    PostViewSet, CommentViewSet, post_detail, 
    add_comment, like_post, like_comment, reply_comment,
    favorite_post, create_post, edit_post, delete_post,
    HomeView, register, profile, edit_profile, favorites
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    
    # 文章相关
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('post/<slug:slug>/edit/', edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', delete_post, name='delete_post'),
    
    # 点赞、收藏和评论
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/favorite/', favorite_post, name='favorite_post'),
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment, name='reply_comment'),
    
    # 用户相关
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('favorites/', favorites, name='my_favorites'),
    
    # API相关
    path('api/', include(router.urls)),
] 