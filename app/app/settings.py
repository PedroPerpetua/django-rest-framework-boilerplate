import logging
from datetime import datetime
from pathlib import Path
from core.extensions.logging import LoggingConfigurationBuilder
from core.utilities import env as env_utils


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# General settings

SECRET_KEY = env_utils.as_string("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_utils.as_bool("DEBUG")
ALLOWED_HOSTS = env_utils.as_list("ALLOWED_HOSTS")


# HTTPS configuration. As per Django documentation, these settings should be enabled if we use HTTPS.
# TODO: Check what they actually do?

HTTPS_ENABLED = env_utils.as_bool("HTTPS_ENABLED")
SESSION_COOKIE_SECURE = HTTPS_ENABLED
CRSF_COOKIE_SECURE = HTTPS_ENABLED


# Cors configuration

CORS_ALLOW_ALL_ORIGINS = env_utils.as_bool("CORS_ALLOW_ALL_ORIGINS")
# If CORS_ALLOW_ALL_ORIGINS is True, this setting is ignored
CORS_ALLOWED_ORIGINS = env_utils.as_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS  # TODO: is this right?


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
    # Our apps here
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
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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


# Logging configuration

LOG_FOLDER = BASE_DIR / 'logs' / datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
# Use our custom log configuration builder to setup the logger
log_config_builder = LoggingConfigurationBuilder() \
    .add_formatter('default', '[{levelname}] {asctime} {module}: {message}')
# Setup the root logger
log_config_builder.add_file_handler('root_handler', LOG_FOLDER / "root.log", formatter='default') \
    .modify_root_logger(handlers=['root_handler'])
# Setup the default Django logger
log_config_builder.add_file_handler('django_handler', LOG_FOLDER / "django.log", formatter='default') \
    .add_logger('django', ['django_handler'], level=logging.DEBUG, propagate=False)
# Setup the default Server logger
log_config_builder.add_file_handler('server_handler', LOG_FOLDER / "server.log", formatter='default') \
    .add_logger('django.server', ['server_handler'], level=logging.DEBUG, propagate=False)
# Add our app-specific loggers
log_config_builder.add_file_handler('core_handler', LOG_FOLDER / 'core.log', formatter='default') \
    .add_logger('core', ['core_handler'], level=logging.DEBUG, propagate=False)
# Finally build the config and assign it.
LOGGING = log_config_builder.build()


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_utils.as_string('POSTGRES_DB'),
        'USER': env_utils.as_string('POSTGRES_USER'),
        'PASSWORD': env_utils.as_string('POSTGRES_PASSWORD'),
        'HOST': env_utils.as_string('POSTGRES_HOST'),
        'PORT': env_utils.as_string('POSTGRES_PORT')
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# File handling

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Rest framework settings

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.exceptions.exception_handler.exception_handler',
}

# User Management

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
