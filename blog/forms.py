from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Profile
from django.utils.text import slugify

class PostForm(forms.ModelForm):
    """文章表单"""
    slug = forms.SlugField(
        max_length=255,
        required=False,
        help_text="文章URL的唯一标识符，只能包含字母、数字、连字符和下划线。该值将用于生成文章的永久链接。",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 使用CharField替代ModelMultipleChoiceField，以适应Tagify组件
    tags = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'category', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # 如果是新建文章且提供了标题，自动生成slug
        if 'data' in kwargs and kwargs['data'].get('title') and not kwargs['data'].get('slug'):
            self.initial['slug'] = slugify(kwargs['data'].get('title'))
        
        # 如果是编辑现有文章，获取该文章的标签
        if self.instance and self.instance.pk:
            instance_tags = self.instance.tags.all()
            if instance_tags:
                # 这里只是为了显示，实际提交时会在视图中处理
                self.initial['tags'] = ','.join([tag.name for tag in instance_tags])
        
    def clean_slug(self):
        """确保slug唯一性，并从标题自动生成slug"""
        slug = self.cleaned_data.get('slug')
        # 如果没有提供slug，则从标题自动生成
        if not slug:
            title = self.cleaned_data.get('title', '')
            if not title:
                raise forms.ValidationError("标题是必填项，无法生成URL别名。")
            slug = slugify(title)
            
        # 检查slug是否已被使用
        if self.instance and self.instance.pk:  # 如果是编辑现有文章
            if Post.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("此URL别名已被使用，请使用其他的。")
        else:  # 如果是新文章
            if Post.objects.filter(slug=slug).exists():
                # 如果已存在，添加一个随机后缀
                import time
                suffix = str(int(time.time()))[-4:]  # 使用时间戳后4位作为后缀
                slug = f"{slug}-{suffix}"
                
        return slug
    
    def clean_tags(self):
        """处理标签字段"""
        # 不进行验证，直接返回原始值，让视图函数处理它
        # Tagify插件会提交JSON格式，我们在视图中解析
        return self.cleaned_data.get('tags', '')


class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # 设置密码输入框的样式
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class UserUpdateForm(forms.ModelForm):
    """用户信息更新表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """用户个人资料更新表单"""
    class Meta:
        model = Profile
        fields = ['bio', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'})
        } 