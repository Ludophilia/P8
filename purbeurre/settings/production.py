"""Django production settings for purbeurre project.""" 

import dj_database_url

from . import *

DEBUG = False
ALLOWED_HOSTS = ["pur8eurre.herokuapp.com"]
MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']

# Database 
DATABASES = { 
    'default': dj_database_url.config(conn_max_age=500)
}

# Simplified static file serving. # https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'