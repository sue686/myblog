import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Post

def generate_slugs():
    posts = Post.objects.filter(slug='')
    count = posts.count()
    
    print(f"找到 {count} 篇没有slug的文章")
    
    for post in posts:
        # save方法会自动生成slug
        post.save()
        print(f"已为文章 '{post.title}' 生成slug: {post.slug}")
    
    print("完成！")

if __name__ == "__main__":
    generate_slugs() 