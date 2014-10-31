# Django settings for room_scheduler project.
import os

DEBUG = False



DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# At some point move these settings into an app where they can be controlled from the admin panel.

GRACE_PERIOD_FOR_SAME_DAY_RESERVATIONS = 15 # in minutes
NO_CANCELATION_PERIOD = 48 # in hours


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)


AUTH_PROFILE_MODULE = 'renters.Renter'

ROOT_URLCONF = 'room_scheduler.urls'

INTERNAL_IPS = ('127.0.0.1',)


TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'room_scheduler.context_processors.globals',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.flatpages',
    #user apps
    'room_scheduler.timeslots',
    'room_scheduler.renters',
    'room_scheduler.overview',
)

try:
    from private_settings import *
except ImportError:
    print """You need to create a private_settings.py file and define a few
settings that I usually stick in a private_settings.py file and leave
out of my repo.  These are: MEDIA_ROOT, MEDIA_URL, ADMIN_MEDIA_PREFIX,
SECRET_KEY
"""

try:
    from local_settings import *
except ImportError:
    pass

