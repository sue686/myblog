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
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Comment posted successfully',
                'comment_id': comment.id
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

def about_me(request):
    """About me page"""
    return render(request, 'blog/about.html')

@login_required
def create_post(request):
    """Create post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Handle slug
            if not post.slug:
                # If no slug provided, generate from title and ensure uniqueness
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = 'post'
                
                # Check if slug already exists
                if Post.objects.filter(slug=base_slug).exists():
                    # Add a random string to ensure uniqueness
                    unique_id = str(uuid.uuid4())[:8]
                    post.slug = f"{base_slug}-{unique_id}"
                else:
                    post.slug = base_slug
            
            post.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    
    return render(request, 'blog/create_post.html', context)

class UserPostListView:
    """User post list view"""
    @classmethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            User = get_user_model()
            
            username = kwargs.get('username')
            user = get_object_or_404(User, username=username)
            
            # Get all published posts by user
            posts = Post.objects.filter(
                author=user,
                is_published=True
            ).select_related('author', 'category').order_by('-created_at')
            
            context = {
                'user_profile': user,
                'posts': posts,
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
    
    # Return JSON response
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': likes_count
    })

@login_required
def reply_comment(request, comment_id):
    """Reply to comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'success': False,
                'message': 'Comment content cannot be empty'
            })
        
        # Create new reply comment
        reply = Comment(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        reply.save()
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Reply successful',
                'comment_id': reply.id
            })
        
        # Non-AJAX requests redirect to post detail page
        return redirect('blog:post_detail', slug=post.slug)
    
    return JsonResponse({
        'success': False,
        'message': 'Please use POST method to submit reply'
    })