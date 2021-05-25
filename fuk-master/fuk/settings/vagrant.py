# Staging server settings

from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fuk_dev',
        'USER': 'django',
        'PASSWORD': 'h0rr1s',
        'HOST': 'localhost',
        'PORT': ''
    }
}
SITE_ID = 1
# use redis cache backend
# database 2 for staging.
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'OPTIONS': {
            'DB': 2,
        },
    },
}
# Paypal

PAYPAL_RECEIVER_EMAIL = "ben.ed_1325863648_biz@mac.com"
#is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://beta.fuk.co.uk"
# how much for a GJ?
SUBSCRIPTION_PRICE="10"


# debugging and local settings.

if DEBUG:
  MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)