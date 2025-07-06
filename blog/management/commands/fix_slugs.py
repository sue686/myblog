from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blog.models import Post, Category, Tag
import re


class Command(BaseCommand):
    help = 'Fix and validate all slugs in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

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

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN - No changes will be made'))
        else:
            self.stdout.write(self.style.SUCCESS('🔧 Fixing slugs...'))
        
        self.stdout.write('=' * 50)

        # 修复文章slug
        self.stdout.write(self.style.SUCCESS('📝 Checking Posts...'))
        posts = Post.objects.all()
        posts_fixed = 0
        
        for post in posts:
            old_slug = post.slug
            new_slug = self.clean_slug(post.title)
            
            if old_slug != new_slug:
                posts_fixed += 1
                self.stdout.write(f'   📄 {post.title}')
                self.stdout.write(f'      Old: {old_slug}')
                self.stdout.write(f'      New: {new_slug}')
                
                if not dry_run:
                    # 确保slug唯一
                    original_slug = new_slug
                    counter = 1
                    while Post.objects.filter(slug=new_slug).exclude(pk=post.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    post.slug = new_slug
                    post.save()
                    self.stdout.write(self.style.SUCCESS(f'      ✅ Updated!'))
                else:
                    self.stdout.write(self.style.WARNING(f'      ⚠️  Would update'))
            else:
                self.stdout.write(f'   ✅ {post.title} - OK')

        # 修复分类slug
        self.stdout.write(self.style.SUCCESS('\n📁 Checking Categories...'))
        categories = Category.objects.all()
        categories_fixed = 0
        
        for category in categories:
            old_slug = category.slug
            new_slug = self.clean_slug(category.name)
            
            if old_slug != new_slug:
                categories_fixed += 1
                self.stdout.write(f'   📁 {category.name}')
                self.stdout.write(f'      Old: {old_slug}')
                self.stdout.write(f'      New: {new_slug}')
                
                if not dry_run:
                    # 确保slug唯一
                    original_slug = new_slug
                    counter = 1
                    while Category.objects.filter(slug=new_slug).exclude(pk=category.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    category.slug = new_slug
                    category.save()
                    self.stdout.write(self.style.SUCCESS(f'      ✅ Updated!'))
                else:
                    self.stdout.write(self.style.WARNING(f'      ⚠️  Would update'))
            else:
                self.stdout.write(f'   ✅ {category.name} - OK')

        # 修复标签slug
        self.stdout.write(self.style.SUCCESS('\n🏷️  Checking Tags...'))
        tags = Tag.objects.all()
        tags_fixed = 0
        
        for tag in tags:
            old_slug = tag.slug
            new_slug = self.clean_slug(tag.name)
            
            if old_slug != new_slug:
                tags_fixed += 1
                self.stdout.write(f'   🏷️  {tag.name}')
                self.stdout.write(f'      Old: {old_slug}')
                self.stdout.write(f'      New: {new_slug}')
                
                if not dry_run:
                    # 确保slug唯一
                    original_slug = new_slug
                    counter = 1
                    while Tag.objects.filter(slug=new_slug).exclude(pk=tag.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    tag.slug = new_slug
                    tag.save()
                    self.stdout.write(self.style.SUCCESS(f'      ✅ Updated!'))
                else:
                    self.stdout.write(self.style.WARNING(f'      ⚠️  Would update'))
            else:
                self.stdout.write(f'   ✅ {tag.name} - OK')

        # 总结
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('📊 Summary:'))
        self.stdout.write(f'   📝 Posts: {posts_fixed} fixed out of {posts.count()}')
        self.stdout.write(f'   📁 Categories: {categories_fixed} fixed out of {categories.count()}')
        self.stdout.write(f'   🏷️  Tags: {tags_fixed} fixed out of {tags.count()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  This was a dry run. Run without --dry-run to apply changes.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✨ All slugs have been fixed!')) 