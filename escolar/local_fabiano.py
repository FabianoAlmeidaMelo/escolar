# coding: utf-8

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'elcolar',
        'USER': 'fabiano',
        'PASSWORD': 'fabiano',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
