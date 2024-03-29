"""
Django settings for mandal project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
from .modeselektor import ArnheimDefaults

# General Debug or Production Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#             _____  _   _ _    _ ______ _____ __  __
#       /\   |  __ \| \ | | |  | |  ____|_   _|  \/  |
#      /  \  | |__) |  \| | |__| | |__    | | | \  / |
#     / /\ \ |  _  /| . ` |  __  |  __|   | | | |\/| |
#    / ____ \| | \ \| |\  | |  | | |____ _| |_| |  | |
#   /_/    \_\_|  \_\_| \_|_|  |_|______|_____|_|  |_|
#                  Arnheim Settings


    
defaults = ArnheimDefaults()


# Zarr Related
ZARR_COMPRESSION = defaults.zarr_compression
ZARR_DTYPE = defaults.zarr_dtype

# Larvik Related
LARVIK_APIVERSION = "0.1"
LARVIK_FILEVERSION = "0.1"




# Postgres Settings
POSTGRES_DB = os.environ.get("POSTGRES_DB", None)
POSTGRES_USER = os.environ.get("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
POSTGRES_HOST =  os.environ.get("POSTGRES_SERVICE_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_SERVICE_PORT_POSTGRESPORT", 5432)


#    _____            _               _
#   |  __ \          (_)             | |
#   | |  | | ___ _ __ ___   _____  __| |
#   | |  | |/ _ \ '__| \ \ / / _ \/ _` |
#   | |__| |  __/ |  | |\ V /  __/ (_| |
#   |_____/ \___|_|  |_| \_/ \___|\__,_|
#       Derived Settings for Django

MEDIA_ROOT = str(defaults.media_path)

# S3 Settings

#S3 Settings
S3_PUBLIC_DOMAIN = defaults.s3_public_domain
AWS_ACCESS_KEY_ID = defaults.s3_key
AWS_SECRET_ACCESS_KEY = defaults.s3_secret
AWS_S3_ENDPOINT_URL  = str(defaults.s3_endpointurl)
AWS_STORAGE_BUCKET_NAME = "test"
AWS_S3_URL_PROTOCOL = defaults.s3_protocol
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_USE_SSL = True
AWS_S3_SECURE_URLS = False # Should resort to True if using in Production behind TLS

ZARR_BUCKET = "zarr"
MEDIA_BUCKET = "media"
FILES_BUCKET = "files"


if defaults.debug:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["web"] + defaults.domains

MEDIA_URL = defaults.media_url
# Overwrite Django Settings
DEBUG = defaults.debug
SECRET_KEY = defaults.secret_key

# SECURITY WARNING: don't run with debug turned on in production!

#Cors Settings and SSL settings
CORS_ORIGIN_ALLOW_ALL = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


STORAGE_MODE = defaults.storage
# Application definition
INSTALLED_APPS = [
    'registration',
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'graphene_django',
    'rest_framework',
    'django_filters',
    'django_extensions',
    'corsheaders',
    'channels',
    'larvik',
    'taggit',
    'social',
    'metamorphers',
    'transformers',
    'evaluators',
    'mutaters',
    'bioconverter',
    'drawing',
    'elements',
    'revamper',
    'flow',
    'answers',
    'test',
    'visualizers',
    'importer',
    'strainers',
    'filters',
]

# Registration Settings
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.


# Channel layer definitions
# http://channels.readthedocs.io/en/latest/topics/channel_layers.html
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation channels_redis
        "BACKEND": defaults.channel_backend,
        "CONFIG": {
            "hosts": [(defaults.channel_host, defaults.channel_port)],
        },
    },
}

# ASGI_APPLICATION should be set to your outermost router
ASGI_APPLICATION = 'mandal.routing.application'

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {
        'read': 'Reading all of your Data ',
        'read_starred': "Reading your shared Data",
        'write': 'Modifying all of your Data',
        'profile': 'Access to your Profile (including Email, Name and Address'}

}

 

# Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

GRAPHENE = {
    'SCHEMA': 'gql.schema.schema', # Where your Graphene schema lives
    'MIDDLEWARE': [
            'graphene_django_extras.ExtraGraphQLDirectiveMiddleware'
        ]
}


GRAPHENE_DJANGO_EXTRAS = {
    'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 50,
    'CACHE_ACTIVE': True,
    'CACHE_TIMEOUT': 300  # seconds
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mandal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'mandal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": defaults.sql_engine,
        "NAME": defaults.db_name,
        "USER": defaults.db_user,
        "PASSWORD":defaults.db_password,
        "HOST": defaults.db_host,
        "PORT": int(defaults.db_port),
        **defaults.db_kwargs
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

LOGIN_REDIRECT_URL = "/"
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': defaults.loglevel,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = defaults.static_path
STATIC_URL = defaults.static_url
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

FIXTURE_DIRS =  [ "fixtures"]

    
