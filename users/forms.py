from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from blog.models import Profile

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '电子邮箱'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # 设置密码输入框的样式
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '密码'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '确认密码'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册')
        return email

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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('该邮箱已被其他用户使用')
        return email

class ProfileUpdateForm(forms.ModelForm):
    """用户个人资料更新表单"""
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'})
        } 