# coding: utf-
import logging

import dj_database_url

"""
Django settings for project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys
from dotenv import load_dotenv


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir
    )
)

DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(DOTENV_PATH)

# Add src to the sys.path if necessary
APPS_DIR = os.path.join(BASE_DIR, 'src')
if APPS_DIR not in sys.path:
    sys.path.append(APPS_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r14mk**_rbgf7%yyogt%vlq(#@-6^yt9$^j)%+a6vzm#70^@e0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'inftybot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='postgres:///')
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# -----------------------------------------------


TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_FACTORY = os.environ.get('TELEGRAM_BOT_FACTORY', 'inftybot.factory.create_bot')
TELEGRAM_BOT_FACTORY_PARAMS = os.environ.get('TELEGRAM_BOT_FACTORY_PARAMS', {
    'token': TELEGRAM_BOT_TOKEN,

})

TELEGRAM_BOT_DISPATCHER_FACTORY = os.environ.get('TELEGRAM_BOT_DISPATCHER_FACTORY',
                                                 'inftybot.factory.create_dispatcher')
TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS = os.environ.get('TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS', {
    'class': 'inftybot.dispatcher.DynamoDispatcher',
    'workers': 1,  # because AWS Lambda is stateless
})

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
SENTRY_LOGGING_LEVEL = os.environ.get('SENTRY_LOGGING_LEVEL', logging.ERROR)
