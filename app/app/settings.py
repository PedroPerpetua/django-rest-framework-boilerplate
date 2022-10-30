from pathlib import Path
from envyaml import EnvYAML # type: ignore

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load our config file
CONFIG = EnvYAML(BASE_DIR / "config.yaml")


# Base config

SECRET_KEY: str = CONFIG['SECRET_KEY']

DEBUG: bool = CONFIG['DEBUG']

ALLOWED_HOSTS: list[str] = CONFIG['ALLOWED_HOSTS']

HTTPS_ENABLED: bool = CONFIG['HTTPS_ENABLED']
SESSION_COOKIE_SECURE = HTTPS_ENABLED
CSRF_COOKIE_SECURE = HTTPS_ENABLED


# Cors config

CORS_ALLOW_ALL_ORIGINS: bool = CONFIG['CORS_ALLOW_ALL_ORIGINS']
CORS_ALLOWED_ORIGINS: list[str] = CONFIG['CORS_ALLOWED_ORIGINS']
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS # TODO: is this right?


# Admin user configuration

ADMIN_USERNAME: str = CONFIG['ADMIN_USERNAME']
ADMIN_EMAIL: str = CONFIG['ADMIN_EMAIL']
ADMIN_PASSWORD: str = CONFIG['ADMIN_PASSWORD']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    # Our apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'core'/'templates'],
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database definition

DATABASES: dict[str, dict[str, str]] = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': CONFIG['POSTGRES_NAME'],
        'USER': CONFIG['POSTGRES_USER'],
        'PASSWORD': CONFIG['POSTGRES_PASSWORD'],
        'HOST': CONFIG['POSTGRES_HOST'],
        'PORT': CONFIG['POSTGRES_PORT']
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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


# File handling

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR/'media'


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
