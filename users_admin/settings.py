"""
Django settings for users_admin project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

from django.conf import ENVIRONMENT_VARIABLE
import utils
from .celery import app as celery_app
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = utils.get_secret('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'multiselectfield',
    'user_profile_api',
    'celery',
    'qrcode'
]

CELERY_BEAT_SCHEDULE = {
       'sincronize-users': {
           'task': 'user_profile_api.tasks.sincronize_users', 
           'schedule': crontab(minute=0, hour='*/4'),
      },   
}

CELERY_ALWAYS_EAGER = False
# Celery Configuration Options
CELERY_TIMEZONE = "America/Argentina/Buenos_Aires"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

JAZZMIN_SETTINGS = {
    "site_title": "Security Admin",
    "site_header": "Library",
    "site_brand": "UNRaf",
    
    # Welcome text on the login screen
    "welcome_sign": "Sistema de seguridad - UNRaf",
    "changeform_format": "collapsible",

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fa fa-user",
        "auth.Group": "fas fa-users",
        "user_profile_api.device": "fas fa-desktop",
        "user_profile_api.room": "fa fa-door-open",
        "user_profile_api.subject": "fa fa-graduation-cap",
        "user_profile_api.userprofile": "fa fa-id-card",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "lumen",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'user_profile_api.middleware.Middleware',
    'user_profile_api.middleware.SpecificPageMiddleware',
]

ROOT_URLCONF = 'users_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'jazzmin/templates')],
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

WSGI_APPLICATION = 'users_admin.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ic3unrafproject',
        'USER': 'root',
        'PASSWORD': utils.get_secret('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'jazzmin/static'),
]

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#AUTH_USER_MODEL = 'user_profile_api.UserProfile'

# Variable to identify environment 'TEST' or 'PROD' (if 'TEST' use mocked requests)
ENVIRONMENT = 'TEST'

print('Environment:', ENVIRONMENT)

# Gateway & Device Settings
#GATEWAY_IP = utils.get_secret('GATEWAY_IP')
#GATEWAY_IP2 = utils.get_secret('GATEWAY_IP2')

GATEWAY_PORT = '85'
GATEWAY_RTSP = '554'
GATEWAY_USER = 'admin'
GATEWAY_PASSWORD = utils.get_secret('GATEWAY_PASSWORD')
DEVICE_UUID = 'D76C6D74-4B20-4BB1-8C4C-B51244DF3026'
GATEWAY_CAMERAS = utils.get_secret('GATEWAY_CAMERAS')
GATEWAY_ONE_CAMERA = utils.get_secret('GATEWAY_ONE_CAMERA')

#BASE_URL = f'{GATEWAY_IP}:{GATEWAY_PORT}'

#MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

