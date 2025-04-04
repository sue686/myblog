import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify

class Profile(models.Model):
    """用户个人资料"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    avatar = models.ImageField(upload_to='profile_pics', default='default.jpg', verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    
    class Meta:
        verbose_name = '个人资料'
        verbose_name_plural = '个人资料'
    
    def __str__(self):
        return f"{self.user.username}的个人资料"

class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
    
    def __str__(self):
        return self.name

class Post(models.Model):
    """博客文章"""
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL别名')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    
    # 存储点赞和收藏的用户
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts', verbose_name='点赞用户')
    favorited_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='favorite_posts', verbose_name='收藏用户')
    
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    recommendation_score = models.FloatField(default=0.0, verbose_name='推荐分数')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 如果slug为空，自动根据标题生成
        if not self.slug:
            self.slug = slugify(self.title)
            
            # 确保slug唯一
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

    def update_recommendation_score(self):
        """更新推荐分数"""
        # 基于浏览量、点赞数、收藏数和评论数的加权计算
        views_weight = 0.3
        likes_weight = 0.3
        favorites_weight = 0.2
        comments_weight = 0.2
        
        total_score = (
            self.views * views_weight +
            self.liked_by.count() * likes_weight +
            self.favorited_by.count() * favorites_weight +
            self.comments.count() * comments_weight
        )
        
        self.recommendation_score = total_score
        self.save()

class Comment(models.Model):
    """文章评论"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_comments', verbose_name='点赞用户')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username}对《{self.post.title}》的评论" 