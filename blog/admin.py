from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Comment, Category, Tag

# 自定义AdminSite
class MyAdminSite(AdminSite):
    site_header = "My Blog Admin"
    site_title = "Blog Admin Portal"
    index_title = "Welcome to Blog Admin"

    def index(self, request, extra_context=None):
        from users.models import User
        from django.contrib.admin.models import LogEntry

        # 统计数据
        total_posts = Post.objects.count()
        total_users = User.objects.count()
        total_comments = Comment.objects.count()
        total_views = Post.objects.aggregate(Sum('views'))['views__sum'] or 0
        categories_count = Category.objects.count()
        tags_count = Tag.objects.count()

        # 最近活动
        recent_posts = Post.objects.select_related('author', 'category').order_by('-created_at')[:5]
        recent_comments = Comment.objects.select_related('author', 'post').order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-date_joined')[:5]
        
        # 发布状态统计
        published_posts = Post.objects.filter(is_published=True).count()
        draft_posts = Post.objects.filter(is_published=False).count()
        
        # 热门文章（按浏览量）
        popular_posts = Post.objects.filter(is_published=True).order_by('-views')[:5]
        
        # 获取最近的管理员操作日志（不进行切片，让模板处理）
        log_entries = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
        
        context = {
            'title': 'Dashboard',
            'total_posts': total_posts,
            'total_users': total_users,
            'total_comments': total_comments,
            'total_views': total_views,
            'total_categories': categories_count,
            'total_tags': tags_count,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'recent_users': recent_users,
            'popular_posts': popular_posts,
            'log_entries': log_entries,  # 添加日志条目
        }
        if extra_context:
            context.update(extra_context)
        return render(request, 'admin/index.html', context)

# 实例化自定义AdminSite
my_admin_site = MyAdminSite()

# 批量操作函数
def make_published(modeladmin, request, queryset):
    """批量发布文章"""
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f'{updated} posts were successfully published.')
make_published.short_description = "✅ Publish selected posts"

def make_unpublished(modeladmin, request, queryset):
    """批量取消发布文章"""
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f'{updated} posts were successfully unpublished.')
make_unpublished.short_description = "📄 Unpublish selected posts"

# ModelAdmin类
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status_badge', 'views', 'created_at']
    list_filter = ['is_published', 'category', 'created_at', 'tags']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'created_at', 'updated_at']
    actions = [make_published, make_unpublished]
    
    fieldsets = (
        ('📝 Post Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('📄 Content', {
            'fields': ('content', 'cover_image')
        }),
        ('⚙️ Settings', {
            'fields': ('is_published',)
        }),
        ('📊 Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_published:
            return format_html(
                '<span class="status-badge status-published">✅ Published</span>'
            )
        else:
            return format_html(
                '<span class="status-badge status-draft">📄 Draft</span>'
            )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新创建的文章
            obj.author = request.user
        super().save_model(request, obj, form, change)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        count = obj.posts.count()
        return format_html(
            '<span class="badge badge-info">📝 {} posts</span>',
            count
        )
    post_count.short_description = 'Posts'

class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        count = obj.posts.count()
        return format_html(
            '<span class="badge badge-primary">🏷️ {} posts</span>',
            count
        )
    post_count.short_description = 'Posts'

class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_title', 'content_preview', 'created_at']
    list_filter = ['created_at', 'post__category']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at']
    
    def post_title(self, obj):
        return format_html(
            '<a href="{}" style="color: #007bff; text-decoration: none;">{}</a>',
            reverse('myadmin:blog_post_change', args=[obj.post.pk]),
            obj.post.title[:50] + '...' if len(obj.post.title) > 50 else obj.post.title
        )
    post_title.short_description = 'Post'
    
    def content_preview(self, obj):
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html(
            '<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{}</div>',
            preview
        )
    content_preview.short_description = 'Content'

# 注册模型到自定义AdminSite
my_admin_site.register(Post, PostAdmin)
my_admin_site.register(Comment, CommentAdmin)
my_admin_site.register(Category, CategoryAdmin)
my_admin_site.register(Tag, TagAdmin)

# 注册用户模型
from users.models import User
from users.admin import CustomUserAdmin
my_admin_site.register(User, CustomUserAdmin)

# 注册Django内置应用（解决auth等应用缺失问题）
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin as DjangoUserAdmin
my_admin_site.register(Group, GroupAdmin)

# 现在只使用自定义 admin 站点 