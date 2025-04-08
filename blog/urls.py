from django.urls import path
from .views import (
    post_detail, add_comment, like_post, like_comment, reply_comment,
    favorite_post, create_post, edit_post, delete_post,
    index, my_favorites, upload_image,
    CategoryListView, CategoryDetailView, SearchResultsView,
    UserPostListView, TagDetailView, about_me
)

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('about/', about_me, name='about_me'),
    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_posts'),
    path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag_posts'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    
    # 文章相关 - 使用slug路径
    path('post/create/', create_post, name='post_create'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', edit_post, name='post_edit'),
    path('post/<slug:slug>/delete/', delete_post, name='post_delete'),
    path('post/<slug:slug>/like/', like_post, name='like_post'),
    path('post/<slug:slug>/favorite/', favorite_post, name='favorite_post'),
    path('post/<slug:slug>/comment/', add_comment, name='add_comment'),
    
    # 添加数字ID支持
    path('post/id/<int:id>/', post_detail, {'by_id': True}, name='post_detail_id'),
    path('post/id/<int:id>/comment/', add_comment, {'by_id': True}, name='add_comment_id'),
    path('post/id/<int:id>/like/', like_post, {'by_id': True}, name='like_post_id'),
    path('post/id/<int:id>/favorite/', favorite_post, {'by_id': True}, name='favorite_post_id'),
    
    # 评论相关
    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/reply/', reply_comment, name='reply_comment'),
    
    # 收藏夹
    path('favorites/', my_favorites, name='my_favorites'),
    
    # 图片上传
    path('upload_image/', upload_image, name='upload_image'),
]