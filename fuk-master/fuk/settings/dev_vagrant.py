# Vagrant dev server settings

from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fuk_dev_vagrant',
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

PAYPAL_RECEIVER_EMAIL = "ben.ed_1325863648_biz@mac.com"
#is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://beta.fuk.co.uk"
# how much for a GJ?
SUBSCRIPTION_PRICE="10"

# debugging and logging settings.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 4

