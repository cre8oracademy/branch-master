from settings.base import *

# For local debugging, we set DEBUG to true and LIVESERVER to True to serve the 
# media files through Django
LOCALSERVER = True
USE_MYSQL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
#  local email, sends to console.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025


SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SITE_ROOT, 'dev.db'),
    }
}

if USE_MYSQL:
  DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'fuk_local',
           'USER': 'django',
           'PASSWORD': 'aslkdjlkjakljelke',
           'HOST': '/tmp/mysql.sock',
       }
   }

  #if we're running the MySQL version, serve static media
  #straight from the live site

  MEDIA_URL = 'http://www.fuk.co.uk/media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# debugging and local settings.

if DEBUG:
  MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# email contact 
ENVELOPE_EMAIL_RECIPIENTS=['ben@widemedia.com']
# # amon logging.
# import amonpy
# MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('amonpy.adapters.DjangoExceptionMiddleware',)