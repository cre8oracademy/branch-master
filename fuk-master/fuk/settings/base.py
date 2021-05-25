# -*- coding: utf-8 -*-
# Django settings for examplesite project.
import os



# Get the relative path to use for template dirs etc.
SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
DEBUG = True
TEMPLATE_DEBUG = DEBUG

  #  DEBUG:
  # import logging
  # logging.basicConfig(
  #     level = logging.DEBUG,
  #     format = '%(asctime)s %(levelname)s %(message)s',
  # )


ADMINS = (
    ('Ben Edwards', 'ben@widemedia.com'),
)
DEFAULT_FROM_EMAIL='fuk@fukmail.co.uk'
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@fuk.mailgun.org'
EMAIL_HOST_PASSWORD = '019f1tj4z2h0'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 465

# New users use Django's default PBKDF2 hasher, but we allow
# for checking old MD5 hashes (which will be upgraded when the 
# user logs in.

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'GMT'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

LANGUAGES = (
    ('en', 'English'),
    ('fr', 'Français'),
)

#LANGUAGE_CODE = 'fr'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.normpath(os.path.join(SITE_ROOT, '../media'))

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.normpath(os.path.join(SITE_ROOT, '../static')) 

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.normpath(os.path.join(SITE_ROOT, '../assets')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '1gzez%G"e42%r(25as*&^*&^hh089+@jL&#)idxt$)$2%0@%+$at7#@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    "fukapp.context_processors.login_block",
    "fukapp.context_processors.user_info",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # our custom middleware for online users.
    'snapboard.middleware.onlinenow.OnlineNowMiddleware',
    # django-pagination for some of the paging.
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)



ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'), 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 600


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.comments',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    # ours
    'snapboard',
    'fukapp',
    'fprofiles',
    # 'fukphotos',
    'fukcomments',
    # 'fuksubs',
    #'git_posthook',
    # third party apps
    'subscription',
    'south',
    'pagination',
    # 'mailer',
    'registration',
    'debug_toolbar',
    'easy_thumbnails',
    'profiles',
    'taggit',
    'smileys',
    'django_extensions',
    'crispy_forms',
    'userena.contrib.umessages',
    'paypal.standard.ipn',
    'micawber',
    'micawber.contrib.mcdjango',
    'envelope',
    # 'johnny',
)

TEST_RUNNER = 'tests.runner.ExcludeAppsTestSuiteRunner'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS':False,
}

# registration uses recaptcha
RECAPTCHA_PUBLIC_KEY = '6LdYMwkAAAAAAPTRZRww9DW_iw736H-_3oSWrxfC'
RECAPTCHA_PRIVATE_KEY = '6LdYMwkAAAAAANjBQB4RVC0qbvvk6PrgojtNZkjW'

# django-registration setting.
ACCOUNT_ACTIVATION_DAYS = 7

# check new signups with StopForumSpam
USE_STOP_FORUM_SPAM = True

# redirect to home page by default on login.
LOGIN_REDIRECT_URL ="/"

# users online settings

ONLINE_THRESHOLD = 60 * 15
ONLINE_MAX = 40

# comments
COMMENTS_APP = 'fukcomments'
COMMENTS_HIDE_REMOVED = True
# profile 
AUTH_PROFILE_MODULE = "fprofiles.UserProfile"

# Avatars.

# Set the widths and heights for the different sized avatars. Not very DRY, as we also need to specify
# sizes in the specs file. 

AVATAR_STANDARD={'width': 120, 'height': 120, 'default': STATIC_URL+'bank/default_profile120.jpg'}
AVATAR_SMALL={'width':84, 'height': 84, 'default': STATIC_URL+'bank/default_profile84.jpg'}

# Settings for easy_thumbnails 

THUMBNAIL_DEBUG = DEBUG

THUMBNAIL_BASEDIR = 'thumbs'

# Micawber embed system http://micawber.readthedocs.org/

MICAWBER_PROVIDERS = 'fukapp.micawber_providers.oembed_providers'
# key is for embedly api.
MICAWBER_DEFAULT_SETTINGS = {
    'key': '26ee36b806f411e1936a4040d3dc5c07',
    'maxwidth': 600,
    'maxheight': 600,
}

#Contact form settings, using django-envelope

ENVELOPE_CONTACT_CHOICES=(
    ('', 'Choose...'),
    (10, 'Advertising enquiry'),
    (20, 'General enquiry'),
)
ENVELOPE_SUBJECT_INTRO='fuk contact form:'
# override as appropriate
ENVELOPE_EMAIL_RECIPIENTS=['tech@widemedia.com']


# Paypal

PAYPAL_RECEIVER_EMAIL = "ben.ed_1325863648_biz@mac.com"
PAYPAL_TEST = DEBUG
#is this only required for django paypal? Should be changed anyway.
SITE_NAME = "http://nu.fuk.co.uk"
# how much for a GJ?
SUBSCRIPTION_PRICE="15"
# django-subscription settings
SUBSCRIPTION_PAYPAL_SETTINGS = {
    "business": PAYPAL_RECEIVER_EMAIL,
    "currency_code": "GBP",

}



# User and forum options

# moderated posts threshold

MODERATED_POST_COUNT=1

# groups settings, groups are created by initial data fixture, so should match here.
POSTGROUPS={"Basics": 1, "Elite": 2, "Newbies": 3}

# how many active threads

ACTIVE_THREAD_COUNT = 20

# how many competitions on comp listing

COMPETITION_LISTING_COUNT = 10

CRISPY_TEMPLATE_PACK = 'uni_form'

# Defaults to MEDIA_URL + 'snapboard/'
SNAP_MEDIA_PREFIX = '/media'


# Read timeout for calculating unread post counts

READ_TIMEOUT = 3600 * 24 * 7

LOCALSERVER = False

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'papertrail': {
            'format': '%(asctime)s basement FUK_DEV: %(message)s',
            'datefmt': '%b %d %H:%M:%S',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'SysLog':{
          'level':'DEBUG',
          'class':'logging.handlers.SysLogHandler',
          'formatter': 'papertrail',
          'address':('logs.papertrailapp.com', 14041)
        }

    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'fukapp': {
            'handlers': ['SysLog'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}




# Mailgun credentials. API key, and should we sign up new users to mailing list.
# See 'mailing' app for more details.
MAILGUN_KEY="key-1dp2fkvc26jxa14s99j67bm81sgvlme7"
# override mailing list name in production
MAILGUN_LIST="testmailing@fukmail.co.uk"
MAILGUN_AUTO_SUB_USERS=True



# statsd settings

# STATSD_HOST = '91.121.161.18'
# STATSD_PORT = 8125
# # override prefix for staging/production
# STATSD_PREFIX = None


#required for debug_toolbar
INTERNAL_IPS = ('127.0.0.1', '88.98.47.129', '86.144.51.241')


