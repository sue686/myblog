from blog.models import Category
from django.utils.text import slugify

# 定义要添加的分类
categories = [
    'Technology', 
    'Travel', 
    'Food', 
    'Health', 
    'Business'
]

# 添加分类
for category_name in categories:
    # 检查分类是否已存在
    if not Category.objects.filter(name=category_name).exists():
        category = Category(
            name=category_name,
            slug=slugify(category_name)
        )
        category.save()
        print(f'Created category: {category_name}')
    else:
        print(f'Category already exists: {category_name}')

# 确认分类已添加
print('\nAll categories:')
for category in Category.objects.all():
    print(f'ID: {category.id}, Name: {category.name}, Slug: {category.slug}') 