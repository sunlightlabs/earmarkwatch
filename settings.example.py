# settings for earmarkwatch project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASE_ENGINE = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''

EMAIL_SUBJECT_PREFIX = '[EarmarkWatch] '


# special database for auth
DBAUTH_HOST = ''
DBAUTH_USER = ''
DBAUTH_PASSWORD = ''
DBAUTH_DATABASE = ''

EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL=''

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False

# absolute path to upload directory
MEDIA_ROOT = '/var/www/sites/django_projects/earmarkwatch_dev/earmarkwatch/static/uploads/'

# URL that handles the media served from MEDIA_ROOT, include trailing /
MEDIA_URL = '/static/uploads/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'earmarkwatch.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.humanize',
    'earmarkwatch.research',
    'earmarkwatch.users',
    #'gatekeeper',
    'sharedauth',
)

AUTHENTICATION_BACKENDS = (
    'sharedauth.authbackend.DatabaseAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/login/'
AUTH_PROFILE_MODULE = 'users.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
