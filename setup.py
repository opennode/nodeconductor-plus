#!/usr/bin/env python

from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2'
]

tests_requires = [
    'factory_boy==2.4.1',
    'mock==1.0.1',
    'six>=1.7.3',
    'django-celery==3.1.16',
]

install_requires = [
    'apache-libcloud>=0.17.0',
    'azure>=0.11.1',
    'nodeconductor>=0.68.0',
    'python-digitalocean>=1.5',
    'python-gitlab>=0.9',
]


setup(
    name='nodeconductor-plus',
    version='0.1.0',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://nodeconductor.com',
    description='NodeConductor Plus is an extension of NodeConductor with extra features',
    long_description=open('README.rst').read(),
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'test': tests_requires,
        'dev': dev_requires,
    },
    entry_points={
        'nodeconductor_extensions': (
            'aws = nodeconductor_plus.aws.urls',
            'azure = nodeconductor_plus.azure.urls',
            'nodeconductor_auth = nodeconductor_plus.nodeconductor_auth.urls',
            'digitalocean = nodeconductor_plus.digitalocean.urls',
            'gitlab = nodeconductor_plus.gitlab.urls',
            'plans = nodeconductor_plus.plans.urls',
            'premium_support = nodeconductor_plus.premium_support.urls',
        ),
        'cost_tracking_strategies': (
            'azure = nodeconductor_plus.azure.cost_tracking:AzureCostTracking',
            'digitalocean = nodeconductor_plus.digitalocean.cost_tracking:DigitalOceanCostTracking',
        ),
    },
    tests_require=tests_requires,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: Other/Proprietary License',
    ],
)
