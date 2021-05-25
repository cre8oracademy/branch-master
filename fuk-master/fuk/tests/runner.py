from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings

class ExcludeAppsTestSuiteRunner(DjangoTestSuiteRunner):
    """Override the default django 'test' command, exclude from testing
    Django and apps from the list below."""

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        if not test_labels:
            # No appnames specified on the command line, so we run all
            # tests, but remove those which don't want to test
            APPS_TO_NOT_RUN = (
              'south',
              'pagination',
              'mailer',
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
              'micawber.contrib.mcdjango',
              'micawber',
              'envelope',
              'raven.contrib.django.raven_compat',
            )
            test_labels = [app for app in settings.INSTALLED_APPS
                            if not app in APPS_TO_NOT_RUN
                            and not app.startswith('django.')]
        return super(ExcludeAppsTestSuiteRunner, self).run_tests(
                                      test_labels, extra_tests, **kwargs)

