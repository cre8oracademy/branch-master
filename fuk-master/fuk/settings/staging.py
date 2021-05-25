
# Staging server settings

from settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'beta.fuk.co.uk',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fuk_staging',
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
        'KEY_PREFIX': 'stage',
       },
}

# Paypal

PAYPAL_RECEIVER_EMAIL = "brad@widemedia.com"
PAYPAL_TEST = DEBUG
#is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://electra.fuk.co.uk"
# django-subscription settings
SUBSCRIPTION_PAYPAL_SETTINGS = {
    "business": PAYPAL_RECEIVER_EMAIL,
    "currency_code": "GBP",

}


SITE_ID = 2

# Don't log to email in staging.
# 

LOGGING['loggers']['django.request']['handlers'] = ['console']
# add sentry settings
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}

STATSD_PREFIX='staging'

# if DEBUG:
#   MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# DEBUG_TOOLBAR_PANELS = (
# 'debug_toolbar.panels.timer.TimerPanel',
# 'debug_toolbar.panels.settings.SettingsPanel',
# 'debug_toolbar.panels.headers.HeadersPanel',
# 'debug_toolbar.panels.request.RequestPanel',
# 'debug_toolbar.panels.sql.SQLPanel',
# 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
# 'debug_toolbar.panels.templates.TemplatesPanel',
# 'debug_toolbar.panels.cache.CachePanel',
# 'debug_toolbar.panels.signals.SignalsPanel',
# 'debug_toolbar.panels.logging.LoggingPanel',
# 'debug_toolbar.panels.redirects.RedirectsPanel',
# )

