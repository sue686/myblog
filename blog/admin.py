from django.contrib import admin
from .models import Category, Tag, Post, Comment
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    
    def post_count(self, obj):
        return obj.post_set.count()
    
    post_count.short_description = '文章数量'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    
    def post_count(self, obj):
        return obj.post_set.count()
    
    post_count.short_description = '文章数量'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'is_published', 'views', 'post_actions')
    list_filter = ('is_published', 'category', 'tags', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)
    
    actions = ['make_published', 'make_draft']
    
    def post_actions(self, obj):
        """为每个帖子添加快速操作按钮"""
        view_url = reverse('blog-detail', kwargs={'slug': obj.slug})
        
        return format_html(
            '<a href="{}" class="button" target="_blank" style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; margin-right: 5px; font-size: 12px;">'
            '<i class="bi bi-eye"></i> 查看</a>',
            view_url,
        )
    
    post_actions.short_description = '操作'
    post_actions.allow_tags = True
    
    def make_published(self, request, queryset):
        """将选中的帖子设为已发布"""
        queryset.update(is_published=True)
    make_published.short_description = "将选中的帖子设为已发布"
    
    def make_draft(self, request, queryset):
        """将选中的帖子设为草稿"""
        queryset.update(is_published=False)
    make_draft.short_description = "将选中的帖子设为草稿"
    
    # 自定义管理员界面
    def changelist_view(self, request, extra_context=None):
        # 添加统计信息到列表页
        if not extra_context:
            extra_context = {}
        extra_context['published_count'] = Post.objects.filter(is_published=True).count()
        extra_context['draft_count'] = Post.objects.filter(is_published=False).count()
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/custom/custom_admin.css',)
        }
        js = ('admin/js/vendor/jquery/jquery.min.js',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'like_count', 'comment_actions')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')
    date_hierarchy = 'created_at'
    
    def like_count(self, obj):
        return obj.liked_by.count()
    
    like_count.short_description = '点赞数'
    
    def comment_actions(self, obj):
        """为每个评论添加快速操作按钮"""
        post_url = reverse('blog-detail', kwargs={'slug': obj.post.slug})
        
        return format_html(
            '<a href="{}#comment-{}" class="button" target="_blank" style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; font-size: 12px;">'
            '<i class="bi bi-eye"></i> 查看</a>',
            post_url, obj.id
        )
    
    comment_actions.short_description = '操作'
    comment_actions.allow_tags = True
    
    class Media:
        css = {
            'all': ('admin/css/custom/custom_admin.css',)
        } 