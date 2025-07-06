import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

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

    def clean_slug(self, text):
        """清理slug，确保只包含允许的字符"""
        # 先使用Django的slugify
        slug = slugify(text)
        # 再次清理，确保只包含字母、数字、连字符和下划线
        slug = re.sub(r'[^a-zA-Z0-9_-]', '', slug)
        # 移除多余的连字符
        slug = re.sub(r'-+', '-', slug)
        # 移除开头和结尾的连字符
        slug = slug.strip('-')
        return slug

    def save(self, *args, **kwargs):
        # 如果slug为空，自动根据标题生成
        if not self.slug:
            self.slug = self.clean_slug(self.title)
            
            # 确保slug唯一
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        else:
            # 如果slug已存在，也要清理一下
            self.slug = self.clean_slug(self.slug)
                
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

class AboutPageContent(models.Model):
    html_content = models.TextField('About页面HTML源码', blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AboutPageContent (updated {self.updated_at})"

# About Me 页面相关模型
class AboutProfile(models.Model):
    """个人基本信息"""
    name = models.CharField(max_length=100, verbose_name='姓名')
    title = models.CharField(max_length=100, verbose_name='职位')
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(max_length=50, verbose_name='电话')
    location = models.CharField(max_length=100, verbose_name='地址')
    linkedin = models.URLField(blank=True, verbose_name='LinkedIn')
    github = models.URLField(blank=True, verbose_name='GitHub')
    twitter = models.URLField(blank=True, verbose_name='Twitter')
    website = models.URLField(blank=True, verbose_name='个人网站')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '个人信息'
        verbose_name_plural = '个人信息'

    def __str__(self):
        return f"{self.name} - {self.title}"

class AboutSummary(models.Model):
    """专业总结"""
    content = models.TextField(verbose_name='专业总结')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '专业总结'
        verbose_name_plural = '专业总结'

    def __str__(self):
        return "专业总结"

class WorkExperience(models.Model):
    """工作经历"""
    position = models.CharField(max_length=100, verbose_name='职位')
    company = models.CharField(max_length=100, verbose_name='公司')
    location = models.CharField(max_length=100, blank=True, verbose_name='地点')
    period = models.CharField(max_length=100, verbose_name='时间段')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '工作经历'
        verbose_name_plural = '工作经历'
        ordering = ['order']

    def __str__(self):
        return f"{self.position} @ {self.company}"

class WorkResponsibility(models.Model):
    """工作职责"""
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE, related_name='responsibilities')
    description = models.TextField(verbose_name='职责描述')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '工作职责'
        verbose_name_plural = '工作职责'
        ordering = ['order']

    def __str__(self):
        return f"{self.experience.position} - {self.description[:50]}"

class SkillGroup(models.Model):
    """技能分组"""
    category = models.CharField(max_length=100, verbose_name='技能类别')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '技能分组'
        verbose_name_plural = '技能分组'
        ordering = ['order']

    def __str__(self):
        return self.category

class SkillItem(models.Model):
    """技能项目"""
    group = models.ForeignKey(SkillGroup, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100, verbose_name='技能名称')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '技能项目'
        verbose_name_plural = '技能项目'
        ordering = ['order']

    def __str__(self):
        return f"{self.group.category} - {self.name}"

class EducationExperience(models.Model):
    """教育经历"""
    degree = models.CharField(max_length=100, verbose_name='学位')
    institution = models.CharField(max_length=100, verbose_name='学校')
    location = models.CharField(max_length=100, blank=True, verbose_name='地点')
    period = models.CharField(max_length=100, blank=True, verbose_name='时间段')
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '教育经历'
        verbose_name_plural = '教育经历'
        ordering = ['order']

    def __str__(self):
        return f"{self.degree} @ {self.institution}"

class EducationProject(models.Model):
    """教育项目"""
    education = models.ForeignKey(EducationExperience, on_delete=models.CASCADE, related_name='projects')
    title = models.TextField(verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '教育项目'
        verbose_name_plural = '教育项目'
        ordering = ['order']

    def __str__(self):
        return f"{self.education.degree} - {self.title[:50]}"

class EducationCourse(models.Model):
    """教育课程"""
    education = models.ForeignKey(EducationExperience, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100, verbose_name='课程名称')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '教育课程'
        verbose_name_plural = '教育课程'
        ordering = ['order']

    def __str__(self):
        return f"{self.education.degree} - {self.name}" 