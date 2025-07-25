import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 修复ALLOWED_HOSTS设置
ALLOWED_HOSTS = [
    'selwyn-blog.duckdns.org',
    '3.26.32.171', 
    'localhost',
    '127.0.0.1',
    '*'  # 临时保留作为备选
]

# CSRF设置 - 修复CSRF验证失败问题
CSRF_TRUSTED_ORIGINS = [
    'https://selwyn-blog.duckdns.org',
    'http://selwyn-blog.duckdns.org',
    'https://3.26.32.171',
    'http://3.26.32.171',
    'http://localhost:8000',
    'https://localhost:8000'
]

# 额外的CSRF配置
CSRF_COOKIE_HTTPONLY = False  # 允许JavaScript访问CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1年

# 添加已安装的应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'corsheaders',
    'widget_tweaks',
    
    # 自定义应用
    'blog',
    'users',
]

# 添加中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS中间件
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_project.urls'
DEBUG_PROPAGATE_EXCEPTIONS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_project.wsgi.application'

# 配置数据库 - 添加SQLite作为备选
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'myblogdb'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # 10分钟
    }
}

# 如果PostgreSQL连接失败，可以切换到SQLite
if DEBUG:
    DATABASES['sqlite'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'  # Changed to English
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 配置媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 配置CORS
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境使用，生产环境应该指定具体的前端域名

# 配置REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# 配置Django Admin
ADMIN_SITE_HEADER = "Blog Management System"
ADMIN_SITE_TITLE = "Blog Admin Panel"
ADMIN_INDEX_TITLE = "Welcome to Blog Management Dashboard"

# 添加管理员界面优化配置
ADMIN_REORDER = (
    ('blog', (
        'Post',
        'Category', 
        'Tag',
        'Comment',
    )),
    ('users', (
        'User',
    )),
    ('auth', (
        'Group',
    )),
)

# 配置用户模型
AUTH_USER_MODEL = 'users.User'

# 登录和登出后的重定向 URL
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'

# 安全设置 - 根据环境调整
USE_HTTPS = os.getenv('USE_HTTPS', 'False').lower() == 'true'

if USE_HTTPS:
    # HTTPS环境的安全设置
    SECURE_SSL_REDIRECT = False  # 让nginx处理重定向
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # HTTP环境的设置（用于调试SSL问题）
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# 会话安全设置
SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF保护
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 两周

# 日志配置（调试用）
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.security.csrf': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    } 