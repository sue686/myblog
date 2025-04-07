import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """用户个人资料"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    website = models.URLField(max_length=200, blank=True, verbose_name='个人网站')
    
    class Meta:
        verbose_name = '个人资料'
        verbose_name_plural = '个人资料'
    
    def __str__(self):
        return f"{self.user.username}的个人资料"
    
    def get_avatar_url(self):
        """获取头像URL，如果没有上传则返回默认头像"""
        # 我们只返回用户的username，让前端直接使用图标字母作为头像
        return None

# 信号：当用户创建时，自动创建关联的个人资料
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """创建用户时创建个人资料"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    """保存用户时保存个人资料"""
    instance.profile.save()

class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name="URL别名")
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 如果slug为空，自动根据名称生成
        if not self.slug:
            self.slug = slugify(self.name)
            
            # 确保slug唯一
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name="URL别名")
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
    
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # 如果slug为空，自动根据名称生成
        if not self.slug:
            self.slug = slugify(self.name)
            
            # 确保slug唯一
            original_slug = self.slug
            counter = 1
            while Tag.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

class Post(models.Model):
    """博客文章"""
    title = models.CharField(max_length=255, verbose_name="标题")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL别名")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name="作者")
    content = models.TextField(verbose_name="内容")
    cover_image = models.ImageField(upload_to='post_covers', blank=True, null=True, verbose_name='封面图片')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="分类")
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name="标签")
    is_published = models.BooleanField(default=False, verbose_name="是否发布")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 社交互动字段
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True, verbose_name="点赞")
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_posts', blank=True, verbose_name="收藏")
    views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    recommendation_score = models.FloatField(default=0, verbose_name="推荐分数")
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '文章'
        verbose_name_plural = '文章'

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
            self.likes.count() * likes_weight +
            self.favorites.count() * favorites_weight +
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
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_comments', verbose_name='点赞用户')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username}对《{self.post.title}》的评论" 