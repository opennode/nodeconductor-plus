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

Add NODECONDUCTOR_INSIGHTS dictionary to NodeConductor settings.
It will contain settings for NodeConductor Plus Insights application.

* PROJECTED_COSTS_EXCESS - used for alerting in insights application, by default equal to 20
