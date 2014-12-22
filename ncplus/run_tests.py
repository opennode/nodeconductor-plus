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
        ROOT_URLCONF='ncauth.urls',
        INSTALLED_APPS=('django.contrib.auth',
                        'django.contrib.contenttypes',
                        'django.contrib.sessions',
                        'django.contrib.admin',
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
