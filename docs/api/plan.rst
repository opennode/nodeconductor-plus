Plan list
---------

To get a list of plans, run GET against **/api/plans/** as authenticated user.

Response example:

.. code-block:: http

    GET /api/plans/ HTTP/1.1

    HTTP/1.0 200 OK
    Content-Type: application/json
    Vary: Accept
    Allow: GET, HEAD, OPTIONS
    X-Result-Count: 1

    [
        {
            "url": "http://example.com/api/plans/290f4d9a892c405ca3ba59257579e87e/",
            "uuid": "290f4d9a892c405ca3ba59257579e87e",
            "name": "Free",
            "price": "0.00",
            "quotas": [
                {
                    "name": "nc_project_count",
                    "value": 2.0
                },
                {
                    "name": "nc_resource_count",
                    "value": 15.0
                },
                {
                    "name": "nc_user_count",
                    "value": 100.0
                }
            ]
        }
    ]


Agreements
----------

To get a list of agreements run GET against **/api/agreements/** as authenticated user.
Agreement can be filtered by customer UUID:

?customer=<customer_UUID>

Response example:

.. code-block:: http

    GET /api/plans/ HTTP/1.1

    HTTP/1.0 200 OK
    Content-Type: application/json
    Vary: Accept
    Allow: GET, HEAD, OPTIONS
    X-Result-Count: 1

    [
        {
            "url": "http://example.com/api/agreements/ab8b6886619849ff9df0e0ebbf16f845/",
            "uuid": "ab8b6886619849ff9df0e0ebbf16f845",
            "state": "active",
            "created": "2015-08-24T15:33:08Z",
            "modified": "2015-08-24T15:33:08Z",
            "approval_url": null,
            "user": null,
            "customer": "http://example.com/api/customers/49d8142299634ecd963afef12d890277/",
            "customer_name": "Walter Lebowski",
            "plan": "http://example.com/api/plans/290f4d9a892c405ca3ba59257579e87e/",
            "plan_name": "Free",
            "plan_price": 0.0,
            "quotas": [
                {
                    "name": "nc_project_count",
                    "value": 2.0
                },
                {
                    "name": "nc_resource_count",
                    "value": 15.0
                },
                {
                    "name": "nc_user_count",
                    "value": 100.0
                }
            ]
        }
    ]


A new agreement can only be created by users with staff privilege (is_staff=True) or customer owners. Example of a valid request:

.. code-block:: http

    POST /api/agreements/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "customer": "http://example.com/api/customers/eb49e5a625f247299bfcf391146bb978/",
        "plan": "http://example.com/api/plans/494e623c83b9476bb5777b536c9d5a30/"
    }

