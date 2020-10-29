"""Django settings for purbeurre project."""

import os

import dj_database_url

# Quick-start development settings - unsuitable for production # See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
IS_PROD_ENV = os.environ.get('ENV') == 'PRODUCTION'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False if IS_PROD_ENV else True

#Allowed hosts
ALLOWED_HOSTS = ["pur8eurre.herokuapp.com"] if IS_PROD_ENV else [] #["*"] pour DEBUG = False

# Application definition
INSTALLED_APPS = [
    'website.apps.WebsiteConfig',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'purbeurre.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'purbeurre.wsgi.application'

# Database # https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pur_beurre',
        'USER': 'P8',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432'
    }
}

if IS_PROD_ENV:
    #dj-database-url # Modify the DATABASE dict default key above to adapt it to heroku 
    DATABASES['default'].update(dj_database_url.config(conn_max_age=500)) # {'NAME': 'dkl...', 'USER': 'ipx...'...}

# Password validation # https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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

# Internationalization # https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = "/signin"

# Static files (CSS, JavaScript, Images) # https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'

#For staticfiles in Heroku. DISABLE_COLLECTSTATIC=1 donc pas de garde "IS_PROD_ENV".
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'),)

# Simplified static file serving. # https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'