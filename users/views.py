from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.models import Post, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.db.models import Count
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def api_register(self, request):
        """API用户注册"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def profile(request, username=None):
    """用户个人资料页面"""
    # 如果username为None，则显示当前登录用户的个人资料
    if username is None:
        username = request.user.username
    
    # 获取用户对象
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 如果用户不存在，重定向到当前用户的个人资料页面
        return redirect('profile')
    
    # 确定是否正在查看自己的个人资料
    is_self = request.user == profile_user
    
    # 获取所有文章
    if is_self or request.user.is_superuser:
        # 如果是自己或超级用户查看，显示所有文章（包括未发布的）
        posts = Post.objects.filter(author=profile_user)
    else:
        # 如果是其他人查看，只显示已发布的文章
        posts = Post.objects.filter(author=profile_user, is_published=True)
    
    # 添加分页
    paginator = Paginator(posts.order_by('-created_at'), 5)  # 每页显示5篇文章
    page = request.GET.get('page')
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，返回第一页
        posts_page = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，返回最后一页
        posts_page = paginator.page(paginator.num_pages)
    
    # 统计数据
    # 1. 计算文章总数
    posts_count = posts.count()
    
    # 2. 计算点赞总数
    total_likes = 0
    for post in posts:
        total_likes += post.likes.count()
    
    # 3. 计算收藏总数
    if is_self:
        # 如果是自己查看，显示自己收藏的文章数量
        total_favorites = Post.objects.filter(favorites=profile_user).count()
    else:
        # 如果是他人查看，统计该用户作品被收藏的次数
        total_favorites = 0
        for post in posts:
            total_favorites += post.favorites.count()
    
    # 调试输出
    print(f"用户 {profile_user.username} 的统计数据:")
    print(f"文章数: {posts_count}")
    print(f"点赞数: {total_likes}")
    print(f"收藏数: {total_favorites}")
    
    # 准备上下文数据
    context = {
        'profile_user': profile_user,
        'is_self': is_self,
        'posts': posts_page,
        'posts_count': posts_count,
        'total_likes': total_likes,
        'total_favorites': total_favorites,
        'title': f"{profile_user.username}的个人资料",
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    # Ensure user has a Profile instance
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Form validation failed. Please check your input.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'title': 'Edit Profile'
    }
    return render(request, 'users/edit_profile.html', context)

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to our community.')
            return redirect('blog:index')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('blog:index')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember_me')
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiration
                if not remember_me:
                    # Set session to expire when browser closes
                    request.session.set_expiry(0)
                    
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect to next page or home
                next_url = request.GET.get('next', 'blog:index')
                return redirect(next_url)
            else:
                # Log authentication failure
                print(f"Login failed for user: {username}")
                messages.error(request, 'Invalid username or password.')
        else:
            # Form validation failed
            print(f"Form errors: {form.errors}")
            messages.error(request, 'Please check your username and password.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('blog:index') 