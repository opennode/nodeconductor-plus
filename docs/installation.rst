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

Configuration
-------------

Add NODECONDUCTOR_PLUS dictionary to NodeConductor settings.
It will contain settings for NodeConductorPlus applications.

* GOOGLE_SECRET - secret key of GooglePlus application (key from test application: 5ivAldGqEv3K5rKZL2QIUfme)
* FACEBOOK_SECRET - secret key of Facebook application (key from test application: fdd9d7ed8cee4a97ff49d2209d3d3db6)
* PROJECTED_COSTS_EXCESS - used for alerting in insights application, by default equal to 20
* USER_ACTIVATION_URL_TEMPLATE - URL template of frontend site, which is used for account activation, for example
  http://example.com/#/activate/{user_uuid}/{token}/
* BILLING_PLAN_APPROVAL_URL - URL template of frontend site, which is used for billing plan approval, for example
  http://example.com/#/approve-billing-plan/'
* BILLING_PLAN_CANCEL_URL - URL template of frontend site, which is used for billing plan approval, for example
  http://example.com/#/cancel-billing-plan/
