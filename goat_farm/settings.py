"""
Django settings for goat_farm project.
"""

import os
from pathlib import Path

# Load environment variables from .env file (if present)
try:
    from dotenv import load_dotenv
    # Explicit path dete hain taaki kisi bhi working directory se sahi .env mile
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=_env_file, override=True)
    print(f"✅ .env loaded: {_env_file} (exists: {_env_file.exists()})")
except ImportError:
    pass  # python-dotenv not installed; rely on system env vars

BASE_DIR = Path(__file__).resolve().parent.parent

# FIX #5: Secret key environment variable se lo — production mein hardcode mat karo
# .env file mein rakho: SECRET_KEY=your-super-secret-key-here
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-in-production-!!!'
)

# FIX #6: DEBUG aur ALLOWED_HOSTS env se lo
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Production mein: DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = _hosts.split(',') if _hosts else ['127.0.0.1', 'localhost']
if DEBUG:
    ALLOWED_HOSTS = ['*']  # Development mein sab allow karo

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ninja',
    'corsheaders',  # ✅ CORS support
    'farm',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ CORS (must be first)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'goat_farm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'goat_farm.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Authentication Settings ──────────────────────────────────────────────────
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Ninja API Config
NINJA_PAGINATION_CLASS = 'ninja.pagination.PageNumberPagination'
NINJA_PAGINATION_PER_PAGE = 50

# ── CORS Configuration ✅ (Auto-configured) ──────────────────
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["DELETE","GET","OPTIONS","PATCH","POST","PUT"]
CORS_ALLOW_HEADERS = [
    "accept","accept-encoding","authorization","content-type",
    "dnt","origin","user-agent","x-csrftoken","x-requested-with",
]

# ── Cache Configuration ──────────────────────────────────────────────────────
# FileBasedCache: disk par store hota hai, server restart ke baad bhi rahega
# No extra packages needed — Django built-in
CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",   # project folder ke andar cache/ folder
        "TIMEOUT":  15 * 60,              # 15 minutes default TTL
        "OPTIONS": {
            "MAX_ENTRIES": 500,
        },
    }
}

# Geo cache (location name) — longer TTL kyunki location naam nahi badlega
WEATHER_CACHE_TTL     = 15 * 60   # 15 min — current weather
FORECAST_CACHE_TTL    = 60 * 60   # 1 hour  — forecast
GEO_CACHE_TTL         = 7 * 24 * 3600  # 7 days — city name

# Weather API Key — .env se load hogi (dotenv ne settings.py mein hi load kiya)
# WeatherService is explicitly reads this Django setting
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
