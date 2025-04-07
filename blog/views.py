from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count, Prefetch
from .models import Post, Category, Tag, Comment
from .serializers import PostSerializer, CommentSerializer
from .forms import PostForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils.text import slugify
from django.db import connection
from django.core.cache import cache
import logging
import time

# 配置日志
logger = logging.getLogger(__name__)

User = get_user_model()

class HomeView(ListView):
    """博客首页视图"""
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """获取文章列表，使用缓存减少数据库查询"""
        # 记录查询性能
        start_time = time.time()
        logger.debug("HomeView.get_queryset被调用")
        
        # 生成缓存键，包含所有筛选条件
        tab = self.request.GET.get('tab', 'latest')
        search_query = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category', '')
        tag_id = self.request.GET.get('tag', '')
        page = self.request.GET.get('page', '1')
        
        cache_key = f"home_posts:{tab}:{search_query}:{category_id}:{tag_id}:{page}"
        queryset = cache.get(cache_key)
        
        if queryset is not None:
            logger.debug(f"缓存命中：{cache_key}")
            # 从缓存恢复实例属性
            self.tab = tab
            self.search_query = search_query
            
            if category_id and category_id.isdigit():
                self.category = get_object_or_404(Category, id=category_id)
            else:
                self.category = None
                
            if tag_id and tag_id.isdigit():
                self.tag = get_object_or_404(Tag, id=tag_id)
            else:
                self.tag = None
                
            # 记录查询性能
            logger.debug(f"HomeView.get_queryset 耗时: {time.time() - start_time:.4f}秒（缓存命中）")
            return queryset
            
        # 缓存未命中，执行查询
        logger.debug(f"缓存未命中：{cache_key}")
        
        # 使用select_related和prefetch_related优化查询
        queryset = Post.objects.filter(is_published=True).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'comments', 'likes', 'favorites'
        )
        
        # 获取选项卡参数
        self.tab = tab
        if self.tab == 'popular':
            # 按热门度排序（浏览量）
            queryset = queryset.order_by('-views', '-created_at')
        elif self.tab == 'trending':
            # 按点赞量排序
            queryset = queryset.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
        else:
            # 默认按最新发布排序
            queryset = queryset.order_by('-created_at')
        
        # 获取搜索查询
        self.search_query = search_query
        if self.search_query:
            queryset = queryset.filter(
                Q(title__icontains=self.search_query) | 
                Q(content__icontains=self.search_query)
            )
        
        # 根据分类筛选
        if category_id and category_id.isdigit():
            self.category = get_object_or_404(Category, id=category_id)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None
        
        # 根据标签筛选
        if tag_id and tag_id.isdigit():
            self.tag = get_object_or_404(Tag, id=tag_id)
            queryset = queryset.filter(tags=self.tag)
        else:
            self.tag = None
        
        # 缓存查询结果，有效期10分钟
        cache.set(cache_key, queryset, 600)
        
        # 记录查询性能
        logger.debug(f"HomeView.get_queryset 耗时: {time.time() - start_time:.4f}秒（执行查询）")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """获取页面上下文数据，添加额外的数据"""
        # 记录查询性能
        start_time = time.time()
        logger.debug("HomeView.get_context_data被调用")
        
        context = super().get_context_data(**kwargs)
        
        # 添加选项卡参数
        context['current_tab'] = self.tab
        
        # 添加搜索查询
        context['search_query'] = self.search_query
        
        # 添加分类和标签数据
        if hasattr(self, 'category') and self.category:
            context['selected_category'] = self.category
        
        if hasattr(self, 'tag') and self.tag:
            context['selected_tag'] = self.tag
            
        # 缓存热门分类和标签，减少数据库查询
        categories = cache.get('all_categories')
        if not categories:
            categories = Category.objects.annotate(
                post_count=Count('posts')
            ).order_by('-post_count')[:10]
            cache.set('all_categories', categories, 3600)  # 缓存1小时
            
        popular_tags = cache.get('popular_tags')
        if not popular_tags:
            popular_tags = Tag.objects.annotate(
                post_count=Count('posts')
            ).order_by('-post_count')[:15]
            cache.set('popular_tags', popular_tags, 3600)  # 缓存1小时
            
        # 缓存精选文章
        recommended_posts = cache.get('recommended_posts')
        if not recommended_posts:
            recommended_posts = Post.objects.filter(
                is_published=True, 
                is_recommended=True
            ).order_by('-recommendation_score')[:5]
            cache.set('recommended_posts', recommended_posts, 1800)  # 缓存30分钟
        
        # 更新上下文
        context['categories'] = categories
        context['popular_tags'] = popular_tags
        context['recommended_posts'] = recommended_posts
        
        # 记录查询性能
        logger.debug(f"HomeView.get_context_data 耗时: {time.time() - start_time:.4f}秒")
        
        return context

class PostViewSet(viewsets.ModelViewSet):
    """博客文章视图集"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        post_id = self.request.query_params.get('post')
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

def post_detail(request, slug):
    """文章详情视图"""
    # 记录性能
    start_time = time.time()
    
    # 从缓存获取文章详情
    cache_key = f"post_detail:{slug}"
    cache_data = cache.get(cache_key)
    
    if cache_data and request.method != 'POST':
        logger.debug(f"缓存命中: {cache_key}")
        context = cache_data
        
        # 即使使用缓存，仍需更新浏览量
        if request.method == 'GET':
            post = get_object_or_404(Post, slug=slug)
            post.views += 1
            post.save(update_fields=['views'])
            # 更新缓存中的浏览量
            context['post'].views = post.views
    else:
        logger.debug(f"缓存未命中: {cache_key}")
        
        # 使用select_related和prefetch_related减少查询次数
        post = get_object_or_404(
            Post.objects.select_related('author', 'category').prefetch_related(
                'tags', 'likes', 'favorites', 
                Prefetch('comments', Comment.objects.filter(parent=None).select_related('author').order_by('-created_at'))
            ), 
            slug=slug
        )
        
        # 仅在GET请求时增加浏览量，防止刷新时多次计数
        if request.method == 'GET':
            post.views += 1
            post.save(update_fields=['views'])  # 只更新views字段，避免修改其他字段
        
        # 获取相关文章
        related_posts = None
        
        # 从缓存获取相关文章
        related_cache_key = f"related_posts:{post.id}"
        related_posts = cache.get(related_cache_key)
        
        if related_posts is None:
            if post.category:
                # 获取同分类的其他文章
                related_posts = Post.objects.filter(
                    category=post.category, 
                    is_published=True
                ).exclude(id=post.id).order_by('-created_at')[:3]
            
            # 如果同分类文章不足3篇，补充最新文章
            if not related_posts or related_posts.count() < 3:
                count_needed = 3 if not related_posts else 3 - related_posts.count()
                additional_posts = Post.objects.filter(
                    is_published=True
                ).exclude(id=post.id)
                
                if related_posts:
                    additional_posts = additional_posts.exclude(id__in=related_posts.values_list('id', flat=True))
                
                additional_posts = additional_posts.order_by('-created_at')[:count_needed]
                
                if related_posts:
                    related_posts = list(related_posts) + list(additional_posts)
                else:
                    related_posts = additional_posts
                    
            # 缓存相关文章，有效期1小时
            cache.set(related_cache_key, related_posts, 3600)
        
        # 构建上下文
        context = {
            'post': post,
            'related_posts': related_posts,
            'comments': post.comments.all(),  # 使用prefetch_related获取的数据
        }
        
        # 缓存文章详情，有效期30分钟
        if request.method == 'GET':
            cache.set(cache_key, context, 1800)
    
    # 记录性能
    logger.debug(f"post_detail 视图耗时: {time.time() - start_time:.4f}秒")
    
    return render(request, 'blog/post_detail.html', context)

@login_required
def add_comment(request, slug):
    """添加评论"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        # 兼容两种字段名称
        content = request.POST.get('body', '') or request.POST.get('content', '')
        content = content.strip()
        
        if not content:
            messages.error(request, 'Comment cannot be empty')
            return redirect('post_detail', slug=post.slug)
        
        comment = Comment(
            post=post,
            author=request.user,
            content=content  # 使用正确的字段名称
        )
        comment.save()
        messages.success(request, 'Comment posted successfully')
        
        # 清除缓存，确保统计数据实时更新
        cache_key = f"user_posts:{post.author.username}"
        cache.delete(cache_key)
        
        # 处理AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Comment posted successfully',
                'comment_id': comment.id
            })
            
    return redirect('blog:post_detail', slug=post.slug)

@login_required
@require_http_methods(["GET", "POST"])
def like_post(request, slug):
    """点赞或取消点赞文章"""
    post = get_object_or_404(Post, slug=slug)
    liked = False
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    # 刷新数据
    likes_count = post.likes.count()
    
    # 更新推荐分数
    try:
        post.recommendation_score = calculate_recommendation_score(post)
        post.save(update_fields=['recommendation_score'])  # 只更新推荐分数字段
    except Exception as e:
        print(f"更新推荐分数错误: {e}")
    
    # 检测是否为AJAX请求
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # 清除缓存，确保数据实时更新
    cache_key = f"user_posts:{post.author.username}"
    cache.delete(cache_key)
    
    if is_ajax:
        return JsonResponse({
            'status': 'liked' if liked else 'unliked',
            'likes_count': likes_count
        })
    
    # 重定向逻辑 - 如果来自用户页面，则返回用户页面
    referer = request.META.get('HTTP_REFERER', '')
    if f'user/{post.author.username}' in referer:
        return redirect('blog:user_posts', username=post.author.username)
    
    return redirect('blog:post_detail', slug=post.slug)

@login_required
@require_http_methods(["GET", "POST"])
def like_comment(request, comment_id):
    """点赞或取消点赞评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 切换点赞状态
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    # 刷新数据
    likes_count = comment.likes.count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'liked' if liked else 'unliked',
            'likes_count': likes_count
        })
    
    return redirect('post_detail', slug=comment.post.slug)

@login_required
def reply_comment(request, comment_id):
    """回复评论"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    
    if request.method == 'POST':
        # 检查是否为AJAX请求
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # 检查内容来源
        if is_ajax and request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        else:
            # 兼容两种字段名称
            content = request.POST.get('body', '') or request.POST.get('content', '')
            content = content.strip()
        
        if not content:
            messages.error(request, 'Reply cannot be empty')
            return redirect('post_detail', slug=post.slug)
        
        reply = Comment(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        reply.save()
        messages.success(request, 'Reply posted successfully')
        
        # 处理AJAX请求
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': 'Reply posted successfully',
                'comment_id': reply.id
            })
            
    return redirect('post_detail', slug=post.slug)

@require_http_methods(["GET", "POST"])
def favorite_post(request, slug):
    """收藏或取消收藏文章"""
    # 使用select_related减少数据库查询
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related('favorites'), 
        slug=slug
    )
    
    # 使用变量存储用户ID，避免重复访问
    user_id = request.user.id
    favorited = False
    
    # 检查缓存中是否存在收藏状态（未实现，如需可添加缓存支持）
    # cache_key = f'favorite_post_{post.id}_{user_id}'
    # cached_result = cache.get(cache_key)
    
    # 检查用户是否已收藏此文章
    if post.favorites.filter(id=user_id).exists():
        post.favorites.remove(request.user)
        favorited = False
    else:
        post.favorites.add(request.user)
        favorited = True
    
    # 刷新收藏计数
    favorites_count = post.favorites.count()
    
    # 异步更新推荐分数（如果可能）
    try:
        # 仅更新必要的字段，减少数据库操作
        post.recommendation_score = calculate_recommendation_score(post)
        post.save(update_fields=['recommendation_score'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"更新推荐分数错误: {e}")
    
    # 检测是否为AJAX请求
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # 如果是AJAX请求，返回JSON响应
    if is_ajax:
        return JsonResponse({
            'status': 'favorited' if favorited else 'removed',
            'favorites_count': favorites_count
        })
    
    # 非AJAX请求，重定向到文章详情页
    return redirect('post_detail', slug=post.slug)

@login_required
def my_favorites(request):
    """显示用户收藏的文章"""
    # 使用prefetch_related获取所有相关数据，减少数据库查询
    favorite_posts = request.user.favorite_posts.select_related(
        'author', 'category'
    ).prefetch_related(
        'tags', 'comments', 'likes'
    ).order_by('-created_at')
    
    # 分页处理
    paginator = Paginator(favorite_posts, 10)  # 每页显示10篇文章
    page = request.GET.get('page', 1)
    
    try:
        favorites = paginator.page(page)
    except PageNotAnInteger:
        favorites = paginator.page(1)
    except EmptyPage:
        favorites = paginator.page(paginator.num_pages)
    
    # 计算不同的分类和作者数量
    categories = set()
    authors = set()
    
    # 获取所有收藏文章的分类和作者统计，不仅限于当前页
    for post in request.user.favorite_posts.all():
        if post.category:
            categories.add(post.category.id)
        authors.add(post.author.id)
    
    context = {
        'favorites': favorites,  # 现在是分页后的结果
        'categories_count': len(categories),
        'authors_count': len(authors),
        'title': 'My Favorites',
        'is_paginated': favorites.has_other_pages(),
        'page_obj': favorites  # 添加分页对象
    }
    
    return render(request, 'blog/favorites.html', context)

@login_required
def create_post(request):
    """Create new post"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            
            # 确保slug存在，如果没有提供则从标题自动生成
            if not form.instance.slug:
                form.instance.slug = slugify(form.instance.title)
                
                # 确保slug唯一性
                if Post.objects.filter(slug=form.instance.slug).exists():
                    import time
                    suffix = str(int(time.time()))[-4:]  # 使用时间戳后4位作为后缀
                    form.instance.slug = f"{form.instance.slug}-{suffix}"
            
            # Save the post first without tags
            post = form.save()
            
            # Handle tags - improved to correctly handle Tagify JSON format
            tags_string = request.POST.get('tags')
            if tags_string:
                try:
                    # Try to parse as JSON (for Tagify format)
                    import json
                    tags_data = json.loads(tags_string)
                    
                    # Handle array of objects with 'value' property
                    if isinstance(tags_data, list):
                        tags_list = []
                        for item in tags_data:
                            if isinstance(item, dict) and 'value' in item:
                                tag_name = item['value'].strip()
                                if tag_name:
                                    tags_list.append(tag_name)
                            elif isinstance(item, str):
                                tag_name = item.strip()
                                if tag_name:
                                    tags_list.append(tag_name)
                    else:
                        # Fallback for non-list JSON
                        tags_list = [tags_data.strip()] if isinstance(tags_data, str) and tags_data.strip() else []
                except json.JSONDecodeError:
                    # Fallback to comma-separated format
                    tags_list = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
                
                # Create or get tags and add to post
                for tag_name in tags_list:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': slugify(tag_name)}
                    )
                    post.tags.add(tag)
            
            # 清除缓存，确保统计数据实时更新
            cache_key = f"user_posts:{request.user.username}"
            cache.delete(cache_key)
            
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            # 添加调试代码，显示表单验证错误
            print("表单验证错误:", form.errors)
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, slug):
    """Edit post"""
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            # Save without m2m fields (tags)
            updated_post = form.save(commit=False)
            
            # 确保slug存在，如果没有提供则从标题自动生成
            if not updated_post.slug:
                updated_post.slug = slugify(updated_post.title)
                
                # 确保slug唯一性
                if Post.objects.filter(slug=updated_post.slug).exclude(pk=updated_post.pk).exists():
                    import time
                    suffix = str(int(time.time()))[-4:]
                    updated_post.slug = f"{updated_post.slug}-{suffix}"
            
            updated_post.save()
            
            # Handle tags - improved to correctly handle Tagify JSON format
            tags_string = request.POST.get('tags')
            
            # Clear existing tags first
            updated_post.tags.clear()
            
            if tags_string:
                try:
                    # Try to parse as JSON (for Tagify format)
                    import json
                    tags_data = json.loads(tags_string)
                    
                    # Handle array of objects with 'value' property
                    if isinstance(tags_data, list):
                        tags_list = []
                        for item in tags_data:
                            if isinstance(item, dict) and 'value' in item:
                                tag_name = item['value'].strip()
                                if tag_name:
                                    tags_list.append(tag_name)
                            elif isinstance(item, str):
                                tag_name = item.strip()
                                if tag_name:
                                    tags_list.append(tag_name)
                    else:
                        # Fallback for non-list JSON
                        tags_list = [tags_data.strip()] if isinstance(tags_data, str) and tags_data.strip() else []
                except json.JSONDecodeError:
                    # Fallback to comma-separated format
                    tags_list = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
                
                # Add tags to post
                for tag_name in tags_list:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'slug': slugify(tag_name)}
                    )
                    updated_post.tags.add(tag)
            
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=updated_post.slug)
        else:
            # 添加调试代码，显示表单验证错误
            print("表单验证错误:", form.errors)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        # 保存作者用户名以便后续清除缓存
        username = post.author.username
        
        # 删除文章
        post.delete()
        
        # 清除缓存，确保统计数据实时更新
        cache_key = f"user_posts:{username}"
        cache.delete(cache_key)
        
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:index')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account {username} created successfully. You can now log in!')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'blog/register.html', {'form': form})

@login_required
def profile(request, username):
    """User profile page"""
    # 获取用户
    user = get_object_or_404(User, username=username)
    
    # 获取用户的所有文章，包括未发布的（如果是当前用户查看自己的文章）
    if request.user == user:
        # 如果是用户自己，显示所有文章（包括草稿）
        posts = Post.objects.filter(author=user).select_related('author', 'category').prefetch_related('tags', 'likes', 'favorites', 'comments')
    else:
        # 如果是其他用户，只显示已发布的文章
        posts = Post.objects.filter(author=user, is_published=True).select_related('author', 'category').prefetch_related('tags', 'likes', 'favorites', 'comments')
    
    # 查询分页 - 每页显示5篇文章
    paginator = Paginator(posts.order_by('-created_at'), 5)
    page = request.GET.get('page', 1)
    
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    
    # 计算统计数据 - 重要修复
    # 获取文章总数（所有文章，不仅限于当前页）
    post_count = posts.count()
    
    # 手动计算点赞和收藏总数
    liked_count = 0
    favorited_count = 0
    
    # 遍历所有文章统计数据
    for post in posts:
        liked_count += post.likes.count()
        favorited_count += post.favorites.count()
    
    # 输出调试信息
    print(f"用户 {username} 的文章统计:")
    print(f"文章数: {post_count}")
    print(f"总点赞数: {liked_count}")
    print(f"总收藏数: {favorited_count}")
    
    # 统计数据添加到上下文
    stats = {
        'post_count': post_count,
        'liked_count': liked_count,
        'favorited_count': favorited_count
    }
    
    context = {
        'profile_user': user,
        'posts': posts_page,
        'stats': stats,
        'is_paginated': paginator.num_pages > 1,
        'title': f"{user.username}的个人主页"
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'users/edit_profile.html', context)

@login_required
def upload_image(request):
    """Upload image (for rich text editor)"""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # Create unique filename
        import uuid
        filename = f"{uuid.uuid4()}.{image.name.split('.')[-1]}"
        
        from django.conf import settings
        import os
        
        # Ensure media/uploads directory exists
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        # Return URL
        url = f"{settings.MEDIA_URL}uploads/{filename}"
        return JsonResponse({'url': url})
    
    return JsonResponse({'error': 'Upload failed'}, status=400)

def calculate_recommendation_score(post):
    """计算文章推荐分数"""
    # 权重设置
    views_weight = 0.3
    likes_weight = 0.3
    favorites_weight = 0.2
    comments_weight = 0.2
    
    # 统计各项数据
    views_count = post.views or 0
    likes_count = post.likes.count()
    favorites_count = post.favorites.count()
    comments_count = post.comments.count()
    
    # 计算总分
    total_score = (
        views_count * views_weight +
        likes_count * likes_weight +
        favorites_count * favorites_weight +
        comments_count * comments_weight
    )
    
    return total_score

class CategoryListView(ListView):
    """分类列表视图"""
    model = Category
    template_name = 'blog/categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(post_count=Count('posts')).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CategoryDetailView(DetailView):
    """
    显示特定分类下的文章
    """
    model = Category
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 打印分类信息用于调试
        category_id = self.object.id
        category_name = self.object.name
        print(f"Category: {category_name}, Category ID: {category_id}")
        
        # 直接从数据库获取该分类下的所有文章
        queryset = Post.objects.filter(
            category=self.object, 
            is_published=True
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'likes', 'comments', 'tags'
        )
        
        print(f"直接查询到的文章数量: {queryset.count()}")
        
        # 排序处理
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'popular':
            queryset = queryset.order_by('-views', '-created_at')
        elif sort == 'comments':
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count', '-created_at')
        elif sort == 'likes': 
            queryset = queryset.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
        else:
            # 默认按最新发布排序
            queryset = queryset.order_by('-created_at')
        
        # 分页处理
        paginator = Paginator(queryset, 12)
        page = self.request.GET.get('page', '1')
        
        try:
            posts = paginator.page(page)
            print(f"当前页文章数量: {len(posts.object_list)}")
            # 打印每篇文章的标题，用于调试
            for post in posts.object_list:
                print(f"文章标题: {post.title}, 作者: {post.author.username}")
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        # 添加到上下文
        context['posts'] = posts
        context['is_paginated'] = paginator.num_pages > 1
        context['current_sort'] = sort
        
        return context

class TagDetailView(DetailView):
    """标签详情视图"""
    model = Tag
    template_name = 'blog/tag_detail.html'
    context_object_name = 'tag'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(tags=self.object, is_published=True).order_by('-created_at')
        paginator = Paginator(posts, 12)
        page = self.request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
            
        context['posts'] = posts
        context['is_paginated'] = True if paginator.num_pages > 1 else False
        context['page_obj'] = posts
        return context

class SearchResultsView(ListView):
    """搜索结果视图"""
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query),
                is_published=True
            ).order_by('-created_at')
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        return context

class UserPostListView(ListView):
    """用户文章列表视图"""
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.view_user = get_object_or_404(User, username=self.kwargs.get('username'))
        
        # 如果是查看自己的文章，显示全部包括草稿
        if self.request.user == self.view_user:
            queryset = Post.objects.filter(author=self.view_user)
        else:
            # 如果是查看他人的文章，只显示已发布的
            queryset = Post.objects.filter(author=self.view_user, is_published=True)
        
        # 获取选项卡参数
        self.tab = self.request.GET.get('tab')
        if self.tab == 'popular':
            # 按热门度排序
            queryset = queryset.order_by('-views', '-created_at')
        elif self.tab == 'oldest':
            # 按最旧发布排序
            queryset = queryset.order_by('created_at')
        else:
            # 默认按最新发布排序
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related('author', 'category').prefetch_related('tags', 'likes', 'comments')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_user'] = self.view_user
        context['tab'] = getattr(self, 'tab', None)
        
        # 设置默认值，确保总是有数据
        context['posts_count'] = 0
        context['total_likes'] = 0 
        context['total_comments'] = 0
        
        try:
            # 获取所有文章（不仅是页面上显示的）
            if self.request.user == self.view_user:
                # 如果是自己查看，计算所有文章（包括草稿）
                all_posts = Post.objects.filter(author=self.view_user)
            else:
                # 查看他人的文章，只计算已发布的
                all_posts = Post.objects.filter(author=self.view_user, is_published=True)
            
            # 文章总数
            posts_count = all_posts.count()
            context['posts_count'] = posts_count
            
            # 如果有文章，计算总点赞和评论数
            if posts_count > 0:
                # 使用预加载优化性能
                all_posts_with_counts = all_posts.prefetch_related('likes', 'comments')
                
                # 计算总点赞和评论数
                likes_count = sum(post.likes.count() for post in all_posts_with_counts)
                comments_count = sum(post.comments.count() for post in all_posts_with_counts)
                
                context['total_likes'] = likes_count
                context['total_comments'] = comments_count
                
                # 输出调试信息
                print(f"用户 {self.view_user.username} 的统计数据:")
                print(f"文章总数: {posts_count}")
                print(f"点赞总数: {likes_count}")
                print(f"评论总数: {comments_count}")
                
        except Exception as e:
            print(f"统计数据计算失败: {str(e)}")
            
            # 出错后尝试简单方法计算
            try:
                # 直接使用现有分页数据
                total_posts = self.object_list.count()
                context['posts_count'] = total_posts
                
                # 如果有文章，手动计算
                if total_posts > 0:
                    likes_count = 0
                    comments_count = 0
                    
                    for post in self.object_list:
                        likes_count += post.likes.count()
                        comments_count += post.comments.count()
                        
                    context['total_likes'] = likes_count
                    context['total_comments'] = comments_count
                
            except Exception as fallback_e:
                print(f"备选统计方法也失败: {str(fallback_e)}")
        
        # 确保值是整数类型
        for key in ['posts_count', 'total_likes', 'total_comments']:
            try:
                context[key] = int(context.get(key, 0))
            except (ValueError, TypeError):
                context[key] = 0
                
        return context
        
    def render_to_response(self, context, **response_kwargs):
        """添加禁止缓存的头部，确保每次都获取最新数据"""
        response = super().render_to_response(context, **response_kwargs)
        
        # 添加控制缓存的请求头
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response

def about_me(request):
    """About Me / Resume page"""
    context = {
        'title': 'About Me',
        'resume': {
            'name': 'Selwyn Liu',
            'email': 'sunrg123@gmail.com',
            'phone': '0432593618',
            'summary': 'Experienced IT Support Officer with a strong background in technical troubleshooting, network security, and system administration. Adept at resolving 50+ IT support tickets per month, ensuring 99% system uptime, and optimizing IT workflows to enhance user experience. Proficient in Active Directory, ITIL Framework, Jira, ServiceNow, and IT asset management. Strong problem-solving, communication, and time management skills, dedicated to providing high-quality IT support and reducing downtime.',
            'experience': [
                {
                    'company': 'Wellington Education Group',
                    'position': 'IT Support Officer',
                    'location': 'Sydney, Australia',
                    'period': '07/2024-Present',
                    'responsibilities': [
                        'Provided IT Help Desk support for 100+ students and staff, reducing downtime by 20%',
                        'Managed network security and IT infrastructure, ensuring 99% system uptime',
                        'Handled 50+ technical support tickets per month, troubleshooting hardware, software, and connectivity issues',
                        'Administered Active Directory, managing user accounts, group policies, and access controls',
                        'Oversaw Google Workspace & Office 365 administration, optimizing email and cloud service performance',
                        'Conducted IT training and onboarding for new employees, reducing onboarding time by 25%',
                        'Maintained IT asset records and inventory, ensuring efficient resource allocation'
                    ]
                },
                {
                    'company': 'Urban Construction Bureau',
                    'position': 'Front-end Developer',
                    'location': 'Henan, China',
                    'period': '11/2022-02/2023',
                    'responsibilities': [
                        'Conducted a thorough analysis of existing web page structures and technical architecture to identify improvement opportunities',
                        'Optimized web content and headlines, increasing search engine visibility by 20%',
                        'Developed responsive web pages using Vue.js, enhancing user experience across multiple devices',
                        'Collaborated with back-end developers, reducing bug reports by 30%. Enhanced code quality and performed data analysis using jQuery',
                        'Managed the content updates and optimization of the Urban Construction Bureau\'s website to ensure accurate information dissemination'
                    ]
                },
                {
                    'company': 'Outsourcing Engineering Company',
                    'position': 'Site Engineer',
                    'location': 'Henan, China',
                    'period': '10/2023-03/2024',
                    'responsibilities': [
                        'Analyzed current processes, labor mobility, and material costs to proposed efficiency improvements and cost reduction strategies, saving 15% on project costs',
                        'Communicated with environmental design engineers to gather feedback and suggestions',
                        'Engaged with site staff to ensure understanding and implementation of best practices'
                    ]
                }
            ],
            'skills': {
                'languages': ['English', 'Mandarin'],
                'technical': [
                    'IT Systems Maintenance & Troubleshooting: Experienced in IT Help Desk support, hardware/software troubleshooting, and IT systems maintenance',
                    'Network Security & Firewall Management: Familiar with TCP/IP, DNS, DHCP, VPN configurations, and network firewall security measures',
                    'Email & Web Hosting Administration: Proficient in managing email hosting (Google Workspace, Office 365) and web hosting services',
                    'Active Directory & User Management: Knowledge in Active Directory setup, user account creation, and permission control',
                    'Cybersecurity & Data Protection: Experience with antivirus software, security patching, and data backup & recovery solutions',
                    'Database: Experienced with MySQL, phpMyAdmin, and database design for web applications',
                    'Hardware & Software: Windows, MacOS, Linux, System Imaging & Deployment'
                ]
            },
            'education': [
                {
                    'university': 'University of Sydney',
                    'degree': 'Master of Information Technology, Major in Software Engineering',
                    'location': 'Sydney, Australia',
                    'period': '02/2022-07/2023',
                    'projects': [
                        {
                            'name': 'Pesticide Guide App',
                            'description': 'Developed a Pesticide Guide App to assist farmers in identifying pesticide information and implementing crop protection measures. The project utilized Vue.js for front-end development and Java to create RESTful APIs. Deployment was carried out using AWS EC2 services.'
                        },
                        {
                            'name': 'Main Project',
                            'description': 'Created a modern web application using Vue.js for the front-end, Spring framework for Java back-end development, and MySQL for database management.'
                        }
                    ],
                    'courses': ['Model-Based Software Engineering', 'Object-Oriented Application Frameworks', 'Visual Analytics', 'Project Management in IT']
                },
                {
                    'university': 'University of RMIT',
                    'degree': 'Bachelor of Information of Technology, Major in Software Engineering',
                    'location': 'Melbourne, Australia',
                    'period': '02/2019-12/2021',
                    'projects': [
                        {
                            'name': 'Campus Delivery System',
                            'description': 'Designed and implemented a delivery system using HTML, CSS, PHP, and phpMyAdmin for backend database management. The system aimed to offer users a streamlined ordering service and provide merchants with an efficient order management platform.'
                        },
                        {
                            'name': 'Main Project in university',
                            'description': 'Developed a hotel web design using Miro for UI design and Vue.js for front-end, while the back-end was implemented using Java Hibernate.'
                        }
                    ],
                    'courses': ['Cloud Computing', 'Professional Computing Practice', 'Programming Project', 'Database Management Systems']
                }
            ]
        }
    }
    return render(request, 'blog/about.html', context) 