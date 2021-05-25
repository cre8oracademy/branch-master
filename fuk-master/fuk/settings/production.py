# Live production settings

from settings.base import *

ALLOWED_HOSTS = [
    "www.fuk.co.uk",
    "fuk.co.uk",
    "212.38.178.9",
]

DEBUG = False
TEMPLATE_DEBUG = DEBUG


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "fuk_production",
        "USER": "django",
        "PASSWORD": "Pz{LTZ77Ws*NXB",
        "HOST": "localhost",
        "PORT": "",
    }
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "KEY_PREFIX": "live",
    },
}

# email

EMAIL_HOST = "smtp.mailgun.org"
EMAIL_HOST_USER = "postmaster@fukmail.co.uk"
EMAIL_HOST_PASSWORD = "rict6ayf"
# Paypal

PAYPAL_RECEIVER_EMAIL = "brad@widemedia.com"
PAYPAL_TEST = False
# is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://www.fuk.co.uk"
SUBSCRIPTION_PAYPAL_SETTINGS = {
    "business": PAYPAL_RECEIVER_EMAIL,
    "currency_code": "GBP",
}

SITE_ID = 3

# Raven for exception tracking

# Set your DSN value
RAVEN_CONFIG = {
    "dsn": "https://1b7eb4bf48fa4aa8867a1a974d8bed00:d7c45e0e6cc64d1d9ece6973dd7fac99@app.getsentry.com/22911",
}
# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + ("raven.contrib.django.raven_compat",)


# log to papertrail in production.

LOGGING["handlers"]["SysLog"] = {
    "level": "INFO",
    "class": "logging.handlers.SysLogHandler",
    "formatter": "simple",
    "address": ("logs.papertrailapp.com", 14041),
}
LOGGING["loggers"]["fukapp"]["handlers"] = ["SysLog"]

# add sentry settings
LOGGING["handlers"]["sentry"] = {
    "level": "ERROR",
    "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
}


# statsd
STATSD_PREFIX = "live"
