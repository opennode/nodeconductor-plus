import sys
from optparse import OptionParser

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

if __name__ == '__main__':
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware'
        ),
        REST_FRAMEWORK = {
            'TEST_REQUEST_DEFAULT_FORMAT': 'json',
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework.authentication.TokenAuthentication',
                'rest_framework.authentication.SessionAuthentication',
            ),
            'DEFAULT_PERMISSION_CLASSES': (
                'rest_framework.permissions.IsAuthenticated',
            ),
            'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
            'DEFAULT_RENDERER_CLASSES': (
                'rest_framework.renderers.JSONRenderer',
            ),
            'PAGINATE_BY_PARAM': 'page_size',
            'MAX_PAGINATE_BY': 100,
            'PAGINATE_BY': 10
        },
        ROOT_URLCONF='ncauth.urls',
        INSTALLED_APPS=('django.contrib.auth',
                        'django.contrib.contenttypes',
                        'django.contrib.sessions',
                        'django.contrib.admin',
                        'rest_framework.authtoken',
                        'ncauth',))

    test_runner = DiscoverRunner(verbosity=1)
    django.setup()

    parser = OptionParser()
    _, args = parser.parse_args()
    if not args:
        args = ['ncauth']
    else:
        # hint for sublime anaconda (and maybe other editors, which allow to run each test separately)
        args = [arg[7:] for arg in args if arg.startswith('ncplus.')]

    failures = test_runner.run_tests(args)
    if failures:
        sys.exit(failures)
