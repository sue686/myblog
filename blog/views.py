from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Post, Category, Tag, Comment
from .serializers import PostSerializer, CommentSerializer
from .forms import PostForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

class HomeView(ListView):
    """博客首页视图"""
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True).order_by('-created_at')
        
        # 获取搜索查询
        self.search_query = self.request.GET.get('q', '')
        if self.search_query:
            queryset = queryset.filter(
                Q(title__icontains=self.search_query) | 
                Q(content__icontains=self.search_query)
            )
        
        # 根据分类筛选
        category_id = self.request.GET.get('category')
        if category_id and category_id.isdigit():
            self.category = get_object_or_404(Category, id=category_id)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None
        
        # 根据标签筛选
        tag_id = self.request.GET.get('tag')
        if tag_id and tag_id.isdigit():
            self.tag = get_object_or_404(Tag, id=tag_id)
            queryset = queryset.filter(tags=self.tag)
        else:
            self.tag = None
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 添加分类列表
        categories = Category.objects.annotate(post_count=Count('post'))
        context['categories'] = categories
        context['category'] = getattr(self, 'category', None)
        
        # 添加标签列表
        tags = Tag.objects.annotate(post_count=Count('post')).order_by('-post_count')[:20]
        context['tags'] = tags
        context['tag'] = getattr(self, 'tag', None)
        
        # 添加搜索查询
        context['search_query'] = getattr(self, 'search_query', '')
        
        # 添加最新文章（侧边栏用）
        context['recent_posts'] = Post.objects.filter(is_published=True).order_by('-created_at')[:5]
        
        # 添加所有文章数量
        context['all_posts_count'] = Post.objects.filter(is_published=True).count()
        
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
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # 增加浏览量
    post.views += 1
    post.save()
    
    # 获取相关文章（同一分类或标签的其他文章）
    related_posts = Post.objects.filter(is_published=True).exclude(id=post.id)
    
    if post.category:
        related_posts = related_posts.filter(category=post.category)
    
    # 如果分类相关文章不足5篇，再加入标签相关文章
    if post.tags.exists() and related_posts.count() < 5:
        tag_related = Post.objects.filter(tags__in=post.tags.all(), is_published=True).exclude(id=post.id)
        if post.category:
            tag_related = tag_related.exclude(category=post.category)
        related_posts = (related_posts | tag_related).distinct()
    
    # 最多展示5篇相关文章
    related_posts = related_posts[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'blog/post_detail.html', context)

@login_required
def add_comment(request, post_id):
    """添加评论"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(request, '评论内容不能为空')
            return redirect('post_detail', slug=post.slug)
        
        comment = Comment(
            post=post,
            author=request.user,
            content=content
        )
        comment.save()
        messages.success(request, '评论发表成功')
        
        # 处理AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': '评论发表成功',
                'comment_id': comment.id
            })
            
    return redirect('post_detail', slug=post.slug)

@login_required
def like_post(request, post_id):
    """点赞文章"""
    post = get_object_or_404(Post, id=post_id)
    
    # 使用ManyToMany关系处理点赞
    if request.user in post.liked_by.all():
        # 已点赞，取消点赞
        post.liked_by.remove(request.user)
        messages.success(request, '已取消点赞')
    else:
        # 未点赞，添加点赞
        post.liked_by.add(request.user)
        messages.success(request, '点赞成功')
    
    # 返回新的点赞数量，用于AJAX请求
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': request.user in post.liked_by.all(),
            'count': post.liked_by.count()
        })
    
    # 普通请求重定向回文章详情页
    return redirect('post_detail', slug=post.slug)

@login_required
def like_comment(request, comment_id):
    """点赞评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    
    # 处理点赞/取消点赞
    if user in comment.liked_by.all():
        comment.liked_by.remove(user)
        liked = False
        message = f'已取消点赞评论'
    else:
        comment.liked_by.add(user)
        liked = True
        message = f'已点赞评论'
    
    # 处理AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success', 
            'liked': liked,
            'count': comment.liked_by.count(),
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def reply_comment(request, comment_id):
    """回复评论"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(request, '回复内容不能为空')
            return redirect('post_detail', slug=post.slug)
        
        reply = Comment(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        reply.save()
        messages.success(request, '回复发表成功')
        
        # 处理AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': '回复发表成功',
                'comment_id': reply.id
            })
            
    return redirect('post_detail', slug=post.slug)

@login_required
def favorite_post(request, post_id):
    """收藏文章"""
    post = get_object_or_404(Post, id=post_id)
    
    # 使用ManyToMany关系处理收藏
    if request.user in post.favorited_by.all():
        # 已收藏，取消收藏
        post.favorited_by.remove(request.user)
        is_favorited = False
        messages.success(request, '已取消收藏')
    else:
        # 未收藏，添加收藏
        post.favorited_by.add(request.user)
        is_favorited = True
        messages.success(request, '收藏成功')
    
    # 返回新的收藏数量，用于AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'favorited': is_favorited,
            'count': post.favorited_by.count()
        })
    
    # 普通请求重定向回文章详情页
    return redirect('post_detail', slug=post.slug)

@login_required
def create_post(request):
    """创建新文章"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # 保存多对多关系（标签）
            messages.success(request, '文章发布成功！')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': '发布文章'})

@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '文章更新成功！')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': '编辑文章'})

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, '文章已删除！')
        return redirect('home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def favorites(request):
    """显示用户收藏的文章"""
    favorite_posts = request.user.favorite_posts.all().order_by('-created_at')
    
    context = {
        'favorite_posts': favorite_posts,
        'title': '我的收藏'
    }
    
    return render(request, 'blog/favorites.html', context)

def register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号 {username} 创建成功，现在可以登录了！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'blog/register.html', {'form': form})

@login_required
def profile(request, username):
    """用户个人资料页面"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'posts': posts
    }
    
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request):
    """编辑用户资料"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '个人资料更新成功！')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'blog/edit_profile.html', context) 