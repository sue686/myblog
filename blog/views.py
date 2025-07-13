from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, Http404
from django.core.cache import cache
from django.db.models import Prefetch
from django.views.decorators.http import require_http_methods
from .models import Post, Comment, Category, Tag
from .forms import PostForm
import time
import logging
from django.db.models import Count
from django.utils.text import slugify
import uuid
from django.contrib.auth import get_user_model
from django.db.models import F
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from .models import AboutPageContent
from django import forms
from django.contrib.auth.decorators import user_passes_test
from .models import (
    AboutProfile, AboutSummary, WorkExperience, WorkResponsibility,
    SkillGroup, SkillItem, EducationExperience, EducationProject, EducationCourse
)
from django.views.decorators.http import require_POST
from django.utils import timezone

# Configure logging
logger = logging.getLogger(__name__)

# Define recommendation score calculation function
def calculate_recommendation_score(post):
    """Calculate article recommendation score"""
    # Simple calculation: views * 0.3 + likes * 0.5 + comments * 0.2
    views_weight = 0.3
    likes_weight = 0.5
    comments_weight = 0.2
    
    views_score = post.views * views_weight
    likes_score = post.likes.count() * likes_weight
    comments_score = post.comments.count() * comments_weight
    
    return views_score + likes_score + comments_score

def post_detail(request, slug=None, id=None, by_id=False):
    """Post detail view"""
    # Record performance
    start_time = time.time()
    
    # Find by ID or slug
    if by_id and id is not None:
        # Find post by ID
        post = get_object_or_404(
            Post.objects.select_related('author', 'category').prefetch_related(
                'tags', 'likes', 'favorites', 
                Prefetch('comments', Comment.objects.filter(parent=None).select_related('author').order_by('-created_at'))
            ), 
            id=id
        )
        cache_key = f"post_detail:id:{id}"
    elif slug is not None:
        # Find post by slug
        post = get_object_or_404(
            Post.objects.select_related('author', 'category').prefetch_related(
                'tags', 'likes', 'favorites', 
                Prefetch('comments', Comment.objects.filter(parent=None).select_related('author').order_by('-created_at'))
            ), 
            slug=slug
        )
        cache_key = f"post_detail:{slug}"
    else:
        # No ID or slug provided, return 404
        raise Http404("Post not found - no identifier provided")
    
    # Get post details from cache
    cache_data = cache.get(cache_key)
    
    if cache_data and request.method != 'POST':
        logger.debug(f"Cache hit: {cache_key}")
        context = cache_data
        
        # Update view count even when using cache
        if request.method == 'GET':
            post.views += 1
            post.save(update_fields=['views'])
            # Update view count in cache
            context['post'].views = post.views
    else:
        logger.debug(f"Cache miss: {cache_key}")
        
        # Only increase view count on GET requests to prevent counting refreshes
        if request.method == 'GET':
            post.views += 1
            post.save(update_fields=['views'])  # Only update views field
        
        # Get related posts
        related_posts = None
        
        # Get related posts from cache
        related_cache_key = f"related_posts:{post.id}"
        related_posts = cache.get(related_cache_key)
        
        if related_posts is None:
            if post.category:
                # Get other posts in the same category
                related_posts = Post.objects.filter(
                    category=post.category, 
                    is_published=True
                ).exclude(id=post.id).order_by('-created_at')[:3]
            
            # If there are fewer than 3 related posts, supplement with latest posts
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
                    
            # Cache related posts for 1 hour
            cache.set(related_cache_key, related_posts, 3600)
        
        # Build context
        context = {
            'post': post,
            'related_posts': related_posts,
            'comments': post.comments.all(),  # Use data from prefetch_related
        }
        
        # Cache post details for 30 minutes
        if request.method == 'GET':
            cache.set(cache_key, context, 1800)
    
    # Record performance
    logger.debug(f"post_detail view time: {time.time() - start_time:.4f} seconds")
    
    return render(request, 'blog/post_detail.html', context)

@login_required
def add_comment(request, slug=None, pk=None, id=None, by_id=False):
    """Add comment"""
    # Record start time for performance tracking
    start_time = time.time()
    
    # Determine how to query the post based on parameters
    if by_id and id is not None:
        post = get_object_or_404(Post, id=id)
        redirect_name = 'blog:post_detail_id'
        redirect_kwargs = {'id': id, 'by_id': True}
    elif pk is not None:
        post = get_object_or_404(Post, pk=pk)
        redirect_name = 'blog:post_detail_by_id'
        redirect_kwargs = {'pk': pk}
    elif slug is not None:
        post = get_object_or_404(Post, slug=slug)
        redirect_name = 'blog:post_detail'
        redirect_kwargs = {'slug': slug}
    else:
        raise Http404("Post not found - no identifier provided")
    
    if request.method == 'POST':
        # Support both field names
        content = request.POST.get('body', '') or request.POST.get('content', '')
        content = content.strip()
        
        if not content:
            messages.error(request, 'Comment cannot be empty')
            return redirect(redirect_name, **redirect_kwargs)
        
        comment = Comment(
            post=post,
            author=request.user,
            content=content  # Use correct field name
        )
        comment.save()
        messages.success(request, 'Comment posted successfully')
        
        # Clear cache to ensure statistics are updated in real-time
        cache_key = f"user_posts:{post.author.username}"
        cache.delete(cache_key)
        
        # Clear post detail cache to immediately show new comment
        if by_id and id is not None:
            post_cache_key = f"post_detail:id:{id}"
        else:
            post_cache_key = f"post_detail:{post.slug}"
        cache.delete(post_cache_key)
        
        # Record and log performance
        processing_time = time.time() - start_time
        logger.debug(f"add_comment processing time: {processing_time:.4f} seconds")
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Comment posted successfully',
                'comment_id': comment.id,
                'processing_time': processing_time,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author_username': comment.author.username,
                    'created_at': comment.created_at.strftime('%B %d, %Y'),
                    'likes_count': 0
                }
            })
        
        # Redirect to post detail page
        return redirect(redirect_name, **redirect_kwargs)

@login_required
@require_http_methods(["GET", "POST"])
def like_post(request, slug=None, id=None, by_id=False):
    """Like or unlike post"""
    # Determine how to query the post based on parameters
    if by_id and id is not None:
        post = get_object_or_404(Post, id=id)
        redirect_name = 'blog:post_detail_id'
        redirect_kwargs = {'id': id, 'by_id': True}
    elif slug is not None:
        post = get_object_or_404(Post, slug=slug)
        redirect_name = 'blog:post_detail'
        redirect_kwargs = {'slug': slug}
    else:
        raise Http404("Post not found - no identifier provided")
    
    liked = False
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    # Refresh data
    likes_count = post.likes.count()
    
    # Update recommendation score
    try:
        if hasattr(post, 'recommendation_score'):
            post.recommendation_score = calculate_recommendation_score(post)
            post.save(update_fields=['recommendation_score'])  # Only update recommendation score field
    except Exception as e:
        logger.error(f"Error updating recommendation score: {e}")
    
    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Clear cache to ensure data is updated in real-time
    cache_key = f"user_posts:{post.author.username}"
    cache.delete(cache_key)
    
    if is_ajax:
        return JsonResponse({
            'status': 'liked' if liked else 'unliked',
            'likes_count': likes_count
        })
    
    # Redirect logic - if from user page, return to user page
    referer = request.META.get('HTTP_REFERER', '')
    if f'user/{post.author.username}' in referer:
        return redirect('blog:user-posts', username=post.author.username)
    
    # Redirect to post detail page
    return redirect(redirect_name, **redirect_kwargs)

@login_required
@require_http_methods(["GET", "POST"])
def favorite_post(request, slug=None, id=None, by_id=False):
    """Favorite or unfavorite post"""
    # Use select_related to reduce database queries
    if by_id and id is not None:
        post = get_object_or_404(
            Post.objects.select_related('author').prefetch_related('favorites'), 
            id=id
        )
        redirect_name = 'blog:post_detail_id'
        redirect_kwargs = {'id': id, 'by_id': True}
    elif slug is not None:
        post = get_object_or_404(
            Post.objects.select_related('author').prefetch_related('favorites'), 
            slug=slug
        )
        redirect_name = 'blog:post_detail'
        redirect_kwargs = {'slug': slug}
    else:
        raise Http404("Post not found - no identifier provided")
    
    # Store user ID in variable to avoid repeated access
    user_id = request.user.id
    favorited = False
    
    # Check if user has already favorited this post
    if post.favorites.filter(id=user_id).exists():
        post.favorites.remove(request.user)
        favorited = False
    else:
        post.favorites.add(request.user)
        favorited = True
    
    # Refresh favorites count
    favorites_count = post.favorites.count()
    
    # Asynchronously update recommendation score
    try:
        if hasattr(post, 'recommendation_score'):
            # Only update necessary fields to reduce database operations
            post.recommendation_score = calculate_recommendation_score(post)
            post.save(update_fields=['recommendation_score'])
    except Exception as e:
        logger.error(f"Error updating recommendation score: {e}")
    
    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # If AJAX request, return JSON response
    if is_ajax:
        return JsonResponse({
            'status': 'favorited' if favorited else 'removed',
            'favorites_count': favorites_count
        })
    
    # Non-AJAX request, redirect to post detail page
    return redirect(redirect_name, **redirect_kwargs)

@login_required
def edit_post(request, slug=None, id=None, by_id=False):
    """Edit post"""
    # Determine how to query the post based on parameters
    if by_id and id is not None:
        post = get_object_or_404(Post, id=id, author=request.user)
        redirect_name = 'blog:post_detail_id'
        redirect_kwargs = {'id': id, 'by_id': True}
    elif slug is not None:
        post = get_object_or_404(Post, slug=slug, author=request.user)
        redirect_name = 'blog:post_detail'
        redirect_kwargs = {'slug': slug}
    else:
        raise Http404("Post not found - no identifier provided")
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            # Save without m2m fields (tags)
            updated_post = form.save()
            
            # Handle tags if needed
            # ... (existing tag handling code)
            
            messages.success(request, 'Post updated successfully!')
            
            # If slug has changed, redirect using the new slug
            if slug is not None and updated_post.slug != slug:
                return redirect('blog:post_detail', slug=updated_post.slug)
            # Otherwise use the original redirect parameters
            return redirect(redirect_name, **redirect_kwargs)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug=None, id=None, by_id=False):
    """Delete post"""
    # Determine how to query the post based on parameters
    if by_id and id is not None:
        post = get_object_or_404(Post, id=id, author=request.user)
    elif slug is not None:
        post = get_object_or_404(Post, slug=slug, author=request.user)
    else:
        raise Http404("Post not found - no identifier provided")
    
    if request.method == 'POST':
        # Save author username for cache clearing
        username = post.author.username
        
        # Delete post
        post.delete()
        
        # Clear cache to ensure statistics are updated in real-time
        cache_key = f"user_posts:{username}"
        cache.delete(cache_key)
        
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:index')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def index(request):
    """Blog homepage"""
    # Get current selected tab
    current_tab = request.GET.get('tab', 'recent')
    
    # Query different post lists based on tab
    if current_tab == 'popular':
        # Sort by view count
        posts = Post.objects.filter(is_published=True).order_by('-views', '-created_at')
    elif current_tab == 'trending':
        # Sort by recommendation score
        posts = Post.objects.filter(is_published=True).order_by('-recommendation_score', '-created_at')
    else:  # Default sort by latest
        posts = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # Optimize query performance
    posts = posts.select_related('author', 'category').prefetch_related('comments', 'likes', 'tags')
    
    # Get popular tags
    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
    
    context = {
        'posts': posts[:12],  # Limit homepage post count
        'tags': tags,
        'current_tab': current_tab
    }
    
    return render(request, 'blog/home.html', context)

class UserPostListView:
    """User post list view"""
    @classmethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            User = get_user_model()
            
            username = kwargs.get('username')
            user = get_object_or_404(User, username=username)
            
            # 获取选项卡参数
            tab = request.GET.get('tab', 'newest')
            
            # Get all published posts by user
            posts_query = Post.objects.filter(
                author=user,
                is_published=True
            ).select_related('author', 'category')
            
            # 根据选项卡排序
            if tab == 'popular':
                posts = posts_query.annotate(
                    popularity=Count('likes') + Count('comments') + F('views')
                ).order_by('-popularity')
            elif tab == 'oldest':
                posts = posts_query.order_by('created_at')
            else:  # newest (default)
                posts = posts_query.order_by('-created_at')
            
            # 计算统计数据
            posts_count = posts_query.count()
            
            # 计算总点赞数
            total_likes = 0
            for post in posts_query:
                total_likes += post.likes.count()
            
            # 计算评论总数
            total_comments = 0
            for post in posts_query:
                total_comments += post.comments.count()
            
            context = {
                'view_user': user,  # 使用view_user而不是user_profile
                'posts': posts,
                'posts_count': posts_count,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'tab': tab,
                'page_title': f'{username}\'s posts'
            }
            
            return render(request, 'blog/user_posts.html', context)
        return view

class CategoryListView:
    """Category list view"""
    @classmethod
    def as_view(cls):
        def view(request):
            from .models import Category, Post
            
            # Get all categories with post count
            categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
            
            # Get latest posts for each category
            for category in categories:
                category.latest_posts = Post.objects.filter(
                    category=category,
                    is_published=True
                ).order_by('-created_at')[:5]
            
            context = {
                'categories': categories
            }
            
            return render(request, 'blog/categories.html', context)
        return view

class CategoryDetailView:
    """Category detail view"""
    @classmethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            from .models import Category, Post
            
            slug = kwargs.get('slug')
            category = get_object_or_404(Category, slug=slug)
            
            # Get all published posts in this category
            posts = Post.objects.filter(
                category=category,
                is_published=True
            ).order_by('-created_at')
            
            context = {
                'category': category,
                'posts': posts
            }
            
            return render(request, 'blog/category_detail.html', context)
        return view

class TagDetailView:
    """Tag detail view"""
    @classmethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            from .models import Tag, Post
            
            slug = kwargs.get('slug')
            tag = get_object_or_404(Tag, slug=slug)
            
            # Get all published posts with this tag
            posts = Post.objects.filter(
                tags=tag,
                is_published=True
            ).select_related('author', 'category').order_by('-created_at')
            
            context = {
                'tag': tag,
                'posts': posts
            }
            
            return render(request, 'blog/tag_detail.html', context)
        return view

class SearchResultsView:
    """Search results view"""
    @classmethod
    def as_view(cls):
        def view(request):
            query = request.GET.get('q', '')
            
            if query:
                # Use Q objects for advanced search
                from django.db.models import Q
                posts = Post.objects.filter(
                    Q(title__icontains=query) | 
                    Q(content__icontains=query) |
                    Q(author__username__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(tags__name__icontains=query),
                    is_published=True
                ).select_related('author', 'category').distinct().order_by('-created_at')
            else:
                posts = Post.objects.none()
            
            context = {
                'query': query,
                'posts': posts,
                'count': posts.count() if query else 0
            }
            
            return render(request, 'blog/search_results.html', context)
        return view

@login_required
def my_favorites(request):
    """My favorites page"""
    # Get all posts favorited by current user
    favorite_posts = Post.objects.filter(
        favorites=request.user,
        is_published=True
    ).select_related('author', 'category').order_by('-created_at')
    
    context = {
        'favorite_posts': favorite_posts,
        'page_title': 'My Favorites'
    }
    
    return render(request, 'blog/my_favorites.html', context)

@login_required
def upload_image(request):
    """Upload image"""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': 'Only JPEG, PNG, GIF or WEBP images are allowed'
            })
        
        # Limit file size (5MB)
        if image.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': 'Image size cannot exceed 5MB'
            })
        
        # Save image
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        
        # Generate file path
        filename = f"user_{request.user.id}_{int(time.time())}_{image.name}"
        path = default_storage.save(f'uploads/{filename}', ContentFile(image.read()))
        
        # Return image URL
        image_url = default_storage.url(path)
        
        return JsonResponse({
            'success': True,
            'file': {
                'url': image_url
            }
        })
        
    return JsonResponse({
        'success': False,
        'message': 'Please provide a valid image file'
    })

@login_required
def like_comment(request, comment_id):
    """Like comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    # Get latest like count
    likes_count = comment.likes.count()
    
    # Clear post detail cache to reflect changes immediately
    post = comment.post
    post_cache_key = f"post_detail:{post.slug}"
    cache.delete(post_cache_key)
    post_id_cache_key = f"post_detail:id:{post.id}"
    cache.delete(post_id_cache_key)
    
    # Return JSON response
    return JsonResponse({
        'success': True,
        'status': 'unliked' if not liked else 'liked',
        'likes_count': likes_count
    })

@login_required
def reply_comment(request, comment_id):
    """Reply to comment"""
    # Record start time for performance tracking
    start_time = time.time()
    
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    
    if request.method == 'POST':
        content = request.POST.get('body', '').strip()
        
        if not content:
            return JsonResponse({
                'success': False,
                'message': '评论内容不能为空'
            })
        
        # Create new reply comment
        reply = Comment(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        reply.save()
        
        # Clear post detail cache to immediately show new reply
        post_cache_key = f"post_detail:{post.slug}"
        cache.delete(post_cache_key)
        
        # Also clear by ID cache if applicable
        post_id_cache_key = f"post_detail:id:{post.id}"
        cache.delete(post_id_cache_key)
        
        # Record and log performance
        processing_time = time.time() - start_time
        logger.debug(f"reply_comment processing time: {processing_time:.4f} seconds")
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': 'success',
                'message': '回复成功',
                'processing_time': processing_time,
                'comment_id': reply.id,
                'reply': {
                    'id': reply.id,
                    'content': reply.content,
                    'author_username': reply.author.username,
                    'created_at': reply.created_at.strftime('%B %d, %Y')
                }
            })
        
        # Non-AJAX requests redirect to post detail page
        return redirect('blog:post_detail', slug=post.slug)
    
    return JsonResponse({
        'success': False,
        'message': '请使用POST方法提交回复'
    })

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard view"""
    User = get_user_model()
    context = {
        'total_posts': Post.objects.count(),
        'total_users': User.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_views': Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0,
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
    }
    return render(request, 'admin/index.html', context)

class AboutPageContentForm(forms.ModelForm):
    class Meta:
        model = AboutPageContent
        fields = ['html_content']
        widgets = {
            'html_content': forms.Textarea(attrs={'rows': 30, 'style': 'font-family:monospace;font-size:1rem;width:100%;'}),
        }

def about_view(request):
    # 查询所有分块数据
    profile = AboutProfile.objects.order_by('-updated_at').first()
    summary = AboutSummary.objects.order_by('-updated_at').first()
    work_experiences_qs = WorkExperience.objects.prefetch_related('responsibilities').order_by('order', '-updated_at')
    work_experiences = []
    for job in work_experiences_qs:
        work_experiences.append({
            'position': job.position,
            'company': job.company,
            'location': job.location,
            'period': job.period,
            'responsibilities': [resp.description for resp in job.responsibilities.all()]
        })
    # 转换技能组为可序列化格式
    skill_groups_qs = SkillGroup.objects.prefetch_related('items').order_by('order')
    skill_groups = []
    for group in skill_groups_qs:
        skill_groups.append({
            'category': group.category,
            'items': [{'name': item.name} for item in group.items.all()]
        })
    
    # 转换教育经历为可序列化格式
    educations_qs = EducationExperience.objects.prefetch_related('projects', 'courses').order_by('order', '-updated_at')
    educations = []
    for edu in educations_qs:
        educations.append({
            'degree': edu.degree,
            'institution': edu.institution,
            'location': edu.location,
            'period': edu.period,
            'projects': [{'title': proj.title} for proj in edu.projects.all()],
            'courses': [{'name': course.name} for course in edu.courses.all()]
        })
    can_edit = request.user.is_authenticated and request.user.is_superuser
    context = {
        'profile': profile,
        'summary': summary,
        'work_experiences': work_experiences,
        'work_experiences_qs': work_experiences_qs,
        'skill_groups': skill_groups,
        'skill_groups_qs': skill_groups_qs,
        'educations': educations,
        'educations_qs': educations_qs,
        'can_edit': can_edit,
    }
    return render(request, 'blog/about.html', context)

@user_passes_test(lambda u: u.is_superuser)
def about_edit_view(request):
    about_obj, _ = AboutPageContent.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = AboutPageContentForm(request.POST, instance=about_obj)
        if form.is_valid():
            form.save()
            return redirect('blog:about')
    else:
        form = AboutPageContentForm(instance=about_obj)
    return render(request, 'blog/about_edit.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_profile_edit_view(request):
    profile = AboutProfile.objects.order_by('-updated_at').first()
    if not profile:
        profile = AboutProfile()
    profile.name = request.POST.get('name', profile.name)
    profile.title = request.POST.get('title', profile.title)
    profile.email = request.POST.get('email', profile.email)
    profile.phone = request.POST.get('phone', profile.phone)
    profile.location = request.POST.get('location', profile.location)
    profile.save()
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_summary_edit_view(request):
    summary = AboutSummary.objects.order_by('-updated_at').first()
    if not summary:
        summary = AboutSummary()
    summary.content = request.POST.get('content', summary.content)
    summary.save()
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_work_edit_view(request, job_id):
    job = get_object_or_404(WorkExperience, id=job_id)
    job.position = request.POST.get('position', job.position)
    job.company = request.POST.get('company', job.company)
    job.location = request.POST.get('location', job.location)
    job.period = request.POST.get('period', job.period)
    job.save()
    # 更新职责
    responsibilities = request.POST.get('responsibilities', '').splitlines()
    job.responsibilities.all().delete()
    for resp in responsibilities:
        resp = resp.strip()
        if resp:
            WorkResponsibility.objects.create(work_experience=job, content=resp)
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_work_delete_view(request, job_id):
    job = get_object_or_404(WorkExperience, id=job_id)
    job.delete()
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_skills_edit_view(request):
    import json
    try:
        data = json.loads(request.POST.get('skills_json', '[]'))
        # 清空原有数据
        SkillGroup.objects.all().delete()
        for group in data:
            group_obj = SkillGroup.objects.create(category=group.get('category', ''))
            for item in group.get('items', []):
                SkillItem.objects.create(group=group_obj, name=item.get('name', str(item)))
        messages.success(request, 'Skills updated successfully!')
    except Exception as e:
        messages.error(request, f'Failed to update skills: {e}')
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_skills_bulk_edit_view(request):
    try:
        categories = request.POST.getlist('categories[]')
        skills_list = request.POST.getlist('skills[]')
        
        # 清空原有数据
        SkillGroup.objects.all().delete()
        
        # 创建新的技能分组
        for i in range(len(categories)):
            if categories[i].strip():  # 只有分类名不为空才创建
                group = SkillGroup.objects.create(
                    category=categories[i].strip(),
                    order=i + 1
                )
                
                # 处理技能项目
                if i < len(skills_list):
                    skills_text = skills_list[i].strip()
                    if skills_text:
                        # 按行分割技能，并清理格式
                        skills = [
                            line.strip() 
                            for line in skills_text.split('\n') 
                            if line.strip()
                        ]
                        
                        for j, skill in enumerate(skills):
                            if skill:
                                SkillItem.objects.create(
                                    group=group,
                                    name=skill,
                                    order=j + 1
                                )
        
        messages.success(request, 'Skills updated successfully!')
    except Exception as e:
        messages.error(request, f'Failed to update skills: {e}')
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_education_edit_view(request):
    import json
    try:
        data = json.loads(request.POST.get('education_json', '[]'))
        # 清空原有数据
        EducationExperience.objects.all().delete()
        for edu in data:
            edu_obj = EducationExperience.objects.create(
                degree=edu.get('degree', ''),
                institution=edu.get('institution', ''),
                location=edu.get('location', ''),
                period=edu.get('period', '')
            )
            for project in edu.get('projects', []):
                EducationProject.objects.create(education=edu_obj, title=project.get('title', ''), description=project.get('description', ''))
            for course in edu.get('courses', []):
                EducationCourse.objects.create(education=edu_obj, name=course.get('name', str(course)))
        messages.success(request, 'Education updated successfully!')
    except Exception as e:
        messages.error(request, f'Failed to update education: {e}')
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_education_bulk_edit_view(request):
    try:
        degrees = request.POST.getlist('degrees[]')
        institutions = request.POST.getlist('institutions[]')
        locations = request.POST.getlist('locations[]')
        periods = request.POST.getlist('periods[]')
        projects_list = request.POST.getlist('projects[]')
        courses_list = request.POST.getlist('courses[]')
        
        # 清空原有数据
        EducationExperience.objects.all().delete()
        
        # 创建新的教育经历
        for i in range(len(degrees)):
            if degrees[i].strip():  # 只有学位不为空才创建
                edu = EducationExperience.objects.create(
                    degree=degrees[i].strip(),
                    institution=institutions[i].strip() if i < len(institutions) else '',
                    location=locations[i].strip() if i < len(locations) else '',
                    period=periods[i].strip() if i < len(periods) else '',
                    order=i + 1
                )
                
                # 处理项目
                if i < len(projects_list):
                    projects_text = projects_list[i].strip()
                    if projects_text:
                        # 按行分割项目
                        projects = [
                            line.strip() 
                            for line in projects_text.split('\n') 
                            if line.strip()
                        ]
                        
                        for j, project in enumerate(projects):
                            if project:
                                # 尝试分割项目标题和描述
                                if ':' in project:
                                    title, description = project.split(':', 1)
                                    title = title.strip()
                                    description = description.strip()
                                else:
                                    title = project
                                    description = ''
                                
                                EducationProject.objects.create(
                                    education=edu,
                                    title=title,
                                    description=description,
                                    order=j + 1
                                )
                
                # 处理课程
                if i < len(courses_list):
                    courses_text = courses_list[i].strip()
                    if courses_text:
                        # 按行分割课程
                        courses = [
                            line.strip() 
                            for line in courses_text.split('\n') 
                            if line.strip()
                        ]
                        
                        for j, course in enumerate(courses):
                            if course:
                                EducationCourse.objects.create(
                                    education=edu,
                                    name=course,
                                    order=j + 1
                                )
        
        messages.success(request, 'Education updated successfully!')
    except Exception as e:
        messages.error(request, f'Failed to update education: {e}')
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_work_add_view(request):
    position = request.POST.get('position', '').strip()
    company = request.POST.get('company', '').strip()
    location = request.POST.get('location', '').strip()
    period = request.POST.get('period', '').strip()
    responsibilities = request.POST.get('responsibilities', '').splitlines()
    if position:
        job = WorkExperience.objects.create(position=position, company=company, location=location, period=period)
        for resp in responsibilities:
            resp = resp.strip()
            if resp:
                WorkResponsibility.objects.create(work_experience=job, content=resp)
    return redirect('blog:about')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def about_work_bulk_edit_view(request):
    try:
        positions = request.POST.getlist('positions[]')
        companies = request.POST.getlist('companies[]')
        locations = request.POST.getlist('locations[]')
        periods = request.POST.getlist('periods[]')
        responsibilities_list = request.POST.getlist('responsibilities[]')
        
        # 清空原有数据
        WorkExperience.objects.all().delete()
        
        # 创建新的工作经历
        for i in range(len(positions)):
            if positions[i].strip():  # 只有职位不为空才创建
                job = WorkExperience.objects.create(
                    position=positions[i].strip(),
                    company=companies[i].strip() if i < len(companies) else '',
                    location=locations[i].strip() if i < len(locations) else '',
                    period=periods[i].strip() if i < len(periods) else '',
                    order=i + 1
                )
                
                # 处理职责
                if i < len(responsibilities_list):
                    responsibilities_text = responsibilities_list[i].strip()
                    if responsibilities_text:
                        # 按行分割职责，并清理格式
                        responsibilities = [
                            line.strip().lstrip('•\t ').strip() 
                            for line in responsibilities_text.split('\n') 
                            if line.strip() and not line.strip().startswith('•\t') == ''
                        ]
                        
                        for j, resp in enumerate(responsibilities):
                            if resp:
                                WorkResponsibility.objects.create(
                                    experience=job,
                                    description=resp,
                                    order=j + 1
                                )
        
        messages.success(request, 'Work experience updated successfully!')
    except Exception as e:
        messages.error(request, f'Failed to update work experience: {e}')
    return redirect('blog:about')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # 自动生成slug
            if not post.slug:
                from django.utils.text import slugify
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = 'post'
                if Post.objects.filter(slug=base_slug).exists():
                    import uuid
                    unique_id = str(uuid.uuid4())[:8]
                    post.slug = f"{base_slug}-{unique_id}"
                else:
                    post.slug = base_slug
            post.save()
            form.save_m2m()
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form, 'categories': Category.objects.all(), 'tags': Tag.objects.all()})

# 临时调试端点 - 检查 CSRF 配置
def debug_csrf_config(request):
    """临时调试端点，检查 CSRF 配置"""
    from django.http import JsonResponse
    from django.conf import settings
    import os
    
    debug_info = {
        'csrf_trusted_origins': getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Not set'),
        'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', 'Not set'),
        'debug': getattr(settings, 'DEBUG', 'Not set'),
        'use_https': getattr(settings, 'USE_HTTPS', 'Not set'),
        'csrf_cookie_secure': getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set'),
        'environment_variables': {
            'CSRF_TRUSTED_ORIGINS': os.getenv('CSRF_TRUSTED_ORIGINS', 'Not set'),
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS', 'Not set'),
            'DEBUG': os.getenv('DEBUG', 'Not set'),
            'USE_HTTPS': os.getenv('USE_HTTPS', 'Not set'),
        },
        'current_origin': request.META.get('HTTP_ORIGIN', 'Not provided'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Not provided'),
        'timestamp': str(timezone.now()) if 'timezone' in globals() else 'timezone not imported'
    }
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})