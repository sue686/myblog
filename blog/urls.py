from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import (
    PostViewSet, CommentViewSet, post_detail, 
    add_comment, like_post, like_comment, reply_comment,
    favorite_post, create_post, edit_post, delete_post,
    HomeView, my_favorites, upload_image,
    CategoryListView, CategoryDetailView, SearchResultsView,
    UserPostListView, TagDetailView, about_me
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

app_name = 'blog'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('about/', about_me, name='about_me'),
    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_posts'),
    path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag_posts'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    
    # 文章相关
    path('post/create/', create_post, name='post_create'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', edit_post, name='post_edit'),
    path('post/<slug:slug>/delete/', delete_post, name='post_delete'),
    
    # 点赞、收藏和评论
    path('post/<slug:slug>/like/', like_post, name='like_post'),
    path('post/<slug:slug>/favorite/', favorite_post, name='favorite_post'),
    path('post/<slug:slug>/comment/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment, name='reply_comment'),
    
    # 收藏夹
    path('favorites/', my_favorites, name='my_favorites'),
    
    # 图片上传
    path('upload_image/', upload_image, name='upload_image'),
    
    # API相关
    path('api/', include(router.urls)),
] 