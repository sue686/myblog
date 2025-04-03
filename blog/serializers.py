from rest_framework import serializers
from .models import Category, Tag, Article, Comment, Like, Favorite
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at', 'likes_count', 'is_liked', 'replies']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'author', 'category', 'tags', 'created_at', 
            'updated_at', 'published_at', 'is_published', 'view_count',
            'comments_count', 'likes_count', 'is_liked', 'is_favorited'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

class ArticleDetailSerializer(ArticleListSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ['content', 'comments']
    
    def get_comments(self, obj):
        # 只获取顶级评论，嵌套评论会通过replies字段获取
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True, context=self.context).data

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False, allow_null=True)
    tags_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'category_id', 'tags_ids', 'is_published']
    
    def create(self, validated_data):
        tags_ids = validated_data.pop('tags_ids', [])
        category_id = validated_data.pop('category_id', None)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                pass
        
        article = Article.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        
        if tags_ids:
            tags = Tag.objects.filter(id__in=tags_ids)
            article.tags.set(tags)
        
        return article
    
    def update(self, instance, validated_data):
        tags_ids = validated_data.pop('tags_ids', None)
        category_id = validated_data.pop('category_id', None)
        
        if category_id is not None:
            try:
                category = Category.objects.get(id=category_id)
                instance.category = category
            except Category.DoesNotExist:
                instance.category = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if tags_ids is not None:
            tags = Tag.objects.filter(id__in=tags_ids)
            instance.tags.set(tags)
        
        instance.save()
        return instance 