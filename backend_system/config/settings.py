import os
import environ
import sys

ROOT_DIR = environ.Path(__file__) - 2  # move up 2 levels to ~/flight_booking_system
BASE_DIR = ROOT_DIR()

env = environ.Env()


SECRET_KEY = env.str('SECRET_KEY', 'fpklsx9d)ru3^kw74ea#93+!qf!qxjl#pi&5x24b+8-8or-9z(')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'lvh.me'])

# Add pytest runner
TEST_RUNNER = 'test_runner.PytestTestRunner'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_rq',
    'rest_framework',
    'authentication',
    'bookings',
    'common',
    'flights',
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

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.backends.CustomTokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.CustomPaginator',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'common.exception_handler.exception_handler'
}

ROOT_URLCONF = 'config.urls'

# rq settings
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 600,
    },
}

# rqscheduler cron jobs
RQ_CRON_JOBS = [
    {
        'cron_string': '0 0 * * *',  # Run at 00:00 daily
        # 'cron_string': '*/2 * * * *',  # Run every 2nd minute
        'func': 'bookings.jobs.travel_date_reminder',
    },
]

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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB_NAME', 'flight_system'),
        'USER': env.str('POSTGRES_DB_USER', 'postgres'),
        'PASSWORD': env.str('POSTGRES_DB_PASSWORD', ''),
        'HOST': env.str('POSTGRES_DB_HOST', 'localhost'),
        'PORT': env.str('POSTGRES_DB_PORT', 5432),
        'OPTIONS': {
            'connect_timeout': 30,
        }
    }
}

DEFAULT_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S %z"

# rq logging
LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': DEFAULT_DATETIME_FORMAT
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
            'filters': ['require_debug_true'],
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'urllib3': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}
# Override the default user model
AUTH_USER_MODEL = 'authentication.User'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'authentication.backends.AuthenticationBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# password duration
PASSWORD_VALIDITY_IN_HOURS = env.int('PASSWORD_VALIDITY_IN_HOURS', 1)

# POSTMARK TOKEN
POSTMARK_TOKEN = env.str('POSTMARK_TOKEN', 'postmark_token')
POSTMARK_SENDER_EMAIL = env.str('POSTMARK_SENDER_EMAIL', 'no_reply@airtech.com')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
