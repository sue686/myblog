from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TagViewSet, ArticleViewSet, CommentViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('tags', TagViewSet)
router.register('articles', ArticleViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 