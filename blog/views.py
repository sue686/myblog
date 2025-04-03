from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Category, Tag, Article, Comment, Like, Favorite
from .serializers import (
    CategorySerializer, TagSerializer, 
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    CommentSerializer
)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    自定义权限：仅允许作者编辑自己的内容
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许文章的作者
        return obj.author == request.user

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_queryset(self):
        queryset = Article.objects.all()
        
        # 非管理员只能看到已发布的文章或自己的文章
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_published=True) | Q(author=self.request.user)
            )
        
        # 根据分类筛选
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # 根据标签筛选
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__id=tag)
        
        # 根据作者筛选
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取文章详情并增加阅读量"""
        instance = self.get_object()
        # 增加阅读量
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞文章"""
        article = self.get_object()
        user = request.user
        
        # 判断是否已点赞
        like, created = Like.objects.get_or_create(
            user=user,
            article=article,
            defaults={'comment': None}
        )
        
        if not created:
            # 如果已点赞，则取消点赞
            like.delete()
            return Response({'detail': '取消点赞成功'}, status=status.HTTP_200_OK)
        
        return Response({'detail': '点赞成功'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """收藏文章"""
        article = self.get_object()
        user = request.user
        
        # 判断是否已收藏
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            article=article
        )
        
        if not created:
            # 如果已收藏，则取消收藏
            favorite.delete()
            return Response({'detail': '取消收藏成功'}, status=status.HTTP_200_OK)
        
        return Response({'detail': '收藏成功'}, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    
    def get_queryset(self):
        article_id = self.request.query_params.get('article')
        if article_id:
            return Comment.objects.filter(article__id=article_id, parent=None)
        return Comment.objects.filter(parent=None)
    
    def create(self, request, *args, **kwargs):
        article_id = request.data.get('article_id')
        parent_id = request.data.get('parent_id')
        content = request.data.get('content')
        
        if not article_id or not content:
            return Response(
                {'detail': '文章ID和评论内容不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response(
                {'detail': '文章不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return Response(
                    {'detail': '父评论不存在'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        comment = Comment.objects.create(
            article=article,
            author=request.user,
            content=content,
            parent=parent
        )
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评论"""
        comment = self.get_object()
        user = request.user
        
        # 判断是否已点赞
        like, created = Like.objects.get_or_create(
            user=user,
            comment=comment,
            defaults={'article': None}
        )
        
        if not created:
            # 如果已点赞，则取消点赞
            like.delete()
            return Response({'detail': '取消点赞成功'}, status=status.HTTP_200_OK)
        
        return Response({'detail': '点赞成功'}, status=status.HTTP_201_CREATED) 