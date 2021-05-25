
# Dev server settings

from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fuk_dev',
        'USER': 'django',
        'PASSWORD': 'Pz{LTZ77Ws*NXB',
        'HOST': 'localhost',
        'PORT': ''
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
       },
}

# Paypal

PAYPAL_RECEIVER_EMAIL = "ben+seller@widemedia.com"
PAYPAL_TEST = DEBUG
#is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://dev.fuk.co.uk"
# how much for a GJ?
SUBSCRIPTION_PRICE="15"
# django-subscription settings
SUBSCRIPTION_PAYPAL_SETTINGS = {
    "business": PAYPAL_RECEIVER_EMAIL,
    "currency_code": "GBP",

}


# debugging and logging settings.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ID = 5


# log fukapp to papertrail

LOGGING['loggers']['fukapp']['handlers']=['SysLog']

# statsd
STATSD_PREFIX='staging'

# if DEBUG:
#   MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware', 'fukapp.middleware.ProfilerMiddleware')