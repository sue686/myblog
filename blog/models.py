from django.db import models
from django.utils import timezone
from users.models import User

class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"

class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    """博客文章"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    def publish(self):
        """发布文章"""
        self.is_published = True
        self.published_at = timezone.now()
        self.save()

class Comment(models.Model):
    """文章评论"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.author.username} on {self.article.title}"

class Like(models.Model):
    """点赞"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(article__isnull=False) & models.Q(comment__isnull=True)) | 
                      (models.Q(article__isnull=True) & models.Q(comment__isnull=False)),
                name='like_either_article_or_comment'
            ),
            models.UniqueConstraint(
                fields=['user', 'article'],
                condition=models.Q(article__isnull=False),
                name='unique_user_article_like'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_user_comment_like'
            )
        ]

class Favorite(models.Model):
    """收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'article'],
                name='unique_user_article_favorite'
            )
        ] 