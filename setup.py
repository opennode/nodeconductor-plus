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
    'nodeconductor>=0.7.0',
]


setup(
    name='nodeconductor-plus',
    version='0.1.0',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://nodeconductor.com',
    description='NodeConductor Plus is an extension of NodeConductor with extra features',
    long_description=open('README.rst').read(),
    package_dir={'': 'ncplus'},
    packages=find_packages('ncplus', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'test': tests_requires,
        'dev': dev_requires,
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
