NodeConductor Plus
==================

NodeConductor Plus is an extension of NodeConductor.


Installation
------------

 * `Install NodeConductor <http://nodeconductor.readthedocs.org/en/latest/guide/intro.html#installation-from-source>`_
 * Clone NodeConductorPlus

  .. code-block:: bash

    git clone git@code.opennodecloud.com:nc-saas/ncplus.git

 * Install NodeConductorPlus into NodeConductor virtual environment

  .. code-block:: bash

    cd /path/to/ncplus/
    python setup.py install

 * Add NodeConductorPlus applications('nodeconductor_plus.nodeconductor_auth') to NodeConductor INSTALLED_APPS
 * Register NodeConductorAuth urls (add next line to server/urls.py urlpatterns):

  .. code:: python

    url(r'^api-auth/', include('nodeconductor_plus.nodeconductor_auth.urls')),

 * Install `django cors  <https://github.com/ottoyiu/django-cors-headers>`_ into NodeConductor virtual environment
 * Configure `django cors  <https://github.com/ottoyiu/django-cors-headers>`_

Configuration
-------------

Add NODECONDUCTOR_PLUS dictionary to NodeConductor settings. It will contain settings for NodeConductorPlus applications.

NodeConductorAuth
^^^^^^^^^^^^^^^^^
 * GOOGLE_SECRET - secret key of GooglePlus application (key from test application: 5ivAldGqEv3K5rKZL2QIUfme)
 * FACEBOOK_SECRET - secret key of Facebook application (key from test application: fdd9d7ed8cee4a97ff49d2209d3d3db6)

