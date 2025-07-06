from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from blog.models import Post, Comment, Category, Tag
from users.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Display blog statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 Blog Statistics Dashboard'))
        self.stdout.write('=' * 50)

        # Basic statistics
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(is_published=True).count()
        draft_posts = Post.objects.filter(is_published=False).count()
        total_users = User.objects.count()
        total_comments = Comment.objects.count()
        total_views = Post.objects.aggregate(Sum('views'))['views__sum'] or 0
        total_categories = Category.objects.count()
        total_tags = Tag.objects.count()

        # Display basic stats
        self.stdout.write(f'📝 Total Posts: {total_posts}')
        self.stdout.write(f'   ✅ Published: {published_posts}')
        self.stdout.write(f'   📄 Drafts: {draft_posts}')
        self.stdout.write(f'👥 Total Users: {total_users}')
        self.stdout.write(f'💬 Total Comments: {total_comments}')
        self.stdout.write(f'👁️  Total Views: {total_views:,}')
        self.stdout.write(f'📁 Categories: {total_categories}')
        self.stdout.write(f'🏷️  Tags: {total_tags}')

        if options['detailed']:
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.SUCCESS('📈 Detailed Statistics'))
            
            # Most popular posts
            popular_posts = Post.objects.filter(is_published=True).order_by('-views')[:5]
            if popular_posts:
                self.stdout.write('\n🔥 Most Popular Posts:')
                for i, post in enumerate(popular_posts, 1):
                    self.stdout.write(f'   {i}. {post.title} ({post.views:,} views)')

            # Recent posts
            recent_posts = Post.objects.order_by('-created_at')[:5]
            if recent_posts:
                self.stdout.write('\n📅 Recent Posts:')
                for post in recent_posts:
                    status = '✅' if post.is_published else '📄'
                    self.stdout.write(f'   {status} {post.title} ({post.created_at.strftime("%Y-%m-%d")})')

            # Category statistics
            categories_with_counts = Category.objects.annotate(
                post_count=Count('posts')
            ).order_by('-post_count')
            
            if categories_with_counts:
                self.stdout.write('\n📁 Categories by Post Count:')
                for category in categories_with_counts:
                    self.stdout.write(f'   {category.name}: {category.post_count} posts')

            # User activity
            active_users = User.objects.annotate(
                post_count=Count('posts'),
                comment_count=Count('comment')  # 修复：使用正确的related_name
            ).order_by('-post_count')[:5]
            
            if active_users:
                self.stdout.write('\n👥 Most Active Users:')
                for user in active_users:
                    self.stdout.write(f'   {user.username}: {user.post_count} posts, {user.comment_count} comments')

            # Recent activity (last 7 days)
            week_ago = timezone.now() - timedelta(days=7)
            recent_posts_count = Post.objects.filter(created_at__gte=week_ago).count()
            recent_comments_count = Comment.objects.filter(created_at__gte=week_ago).count()
            
            self.stdout.write('\n📈 Activity (Last 7 Days):')
            self.stdout.write(f'   New Posts: {recent_posts_count}')
            self.stdout.write(f'   New Comments: {recent_comments_count}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✨ Statistics generated successfully!')) 